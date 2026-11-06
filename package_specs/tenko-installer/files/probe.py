"""Live-system probing and safety checks.

This module executes read-only commands through the command runner and turns
their output into the pure data structures in :mod:`disk`.  It is the only
place that knows how to find the live installation medium, decide whether a
disk is in use, and read a partition table from a real device.
"""

from __future__ import annotations

import os
import shutil
import stat
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, replace
from typing import Iterable, Sequence

import disk
from disk import Disk, PartitionTable, parse_lsblk_json, parse_sfdisk_json
from runner import CommandError, CommandRunner

MIB = 1024 * 1024
GIB = 1024 * MIB

LSBLK_FIELDS = (
    "NAME,KNAME,PATH,TYPE,SIZE,RO,MODEL,SERIAL,TRAN,PTTYPE,PARTN,"
    "PARTUUID,UUID,FSTYPE,LABEL,MOUNTPOINTS,LOG-SEC,PHY-SEC"
)

REQUIRED_TOOLS = (
    "lsblk",
    "sfdisk",
    "blkid",
    "wipefs",
    "blockdev",
    "partx",
    "udevadm",
    "mkfs.fat",
    "fsck.fat",
    "mke2fs",
    "e2fsck",
    "mkfs.btrfs",
    "btrfs",
    "mkswap",
    "swapon",
    "swapoff",
    "dnf",
    "rpm",
    "bootctl",
    "efibootmgr",
    "dracut",
    "chroot",
    "useradd",
    "groupadd",
    "chpasswd",
    "passwd",
    "mount",
    "umount",
    "findmnt",
    "install",
    "sync",
)

TOOL_PATH = "/usr/sbin:/usr/bin:/sbin:/bin"


class ProbeError(RuntimeError):
    pass


def _repository_reachable(repodata: str) -> tuple[bool, str]:
    """True if the repository metadata exists locally or can be fetched.

    A network repository is retried for a while: the installer starts as
    soon as the live system reaches multi-user, which can be before DHCP
    has finished, and a URL is not a path that os.path.isfile() can see.

    The public repository sits behind Cloudflare, which returns HTTP 403 to
    the default ``Python-urllib`` User-Agent while dnf's UA is allowed.  Send
    a product UA so the preflight probes the same bytes dnf will fetch.
    """
    if "://" not in repodata:
        return os.path.isfile(repodata), repodata
    last = "not fetched"
    request_headers = {
        "User-Agent": "Tenko-Installer/13.1",
        "Accept": "*/*",
    }
    for _ in range(6):
        try:
            request = urllib.request.Request(repodata, headers=request_headers)
            with urllib.request.urlopen(request, timeout=15) as response:
                if response.status == 200:
                    return True, repodata
                last = "HTTP %s" % response.status
        except urllib.error.HTTPError as exc:
            last = "HTTP %s %s" % (exc.code, exc.reason)
        except (urllib.error.URLError, OSError) as exc:
            last = str(exc)
        time.sleep(5)
    return False, "%s (%s)" % (repodata, last)


@dataclass(frozen=True)
class Check:
    ok: bool
    label: str
    detail: str = ""


@dataclass(frozen=True)
class ProbedDisk:
    disk: Disk
    table: PartitionTable | None
    live: bool = False
    selectable: bool = False
    reasons: tuple[str, ...] = ()

    @property
    def name(self) -> str:
        return self.disk.path


def _read_text(path: str) -> str:
    """Read a small text file; never read a device, FIFO or socket.

    /run/initramfs/livedev is a symlink to the live block device on some
    dracut versions; following it would read the whole ISO into memory.
    """
    try:
        if not stat.S_ISREG(os.stat(path).st_mode):
            return ""
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def _read_dir(path: str) -> list[str]:
    try:
        return sorted(os.listdir(path))
    except OSError:
        return []


def _mount_sources() -> dict[str, str]:
    """Return source -> mountpoint from /proc/mounts."""

    result: dict[str, str] = {}
    for line in _read_text("/proc/mounts").splitlines():
        fields = line.split()
        if len(fields) >= 2:
            result[fields[0]] = fields[1]
    return result


def _swap_sources() -> set[str]:
    sources: set[str] = set()
    for line in _read_text("/proc/swaps").splitlines()[1:]:
        fields = line.split()
        if fields:
            sources.add(fields[0])
    return sources


def _mdstat() -> str:
    return _read_text("/proc/mdstat")


def _holders(kname: str) -> list[str]:
    return _read_dir(f"/sys/class/block/{kname}/holders")


MIN_TARGET_BYTES = 1024 * MIB


def _device_class_reasons(probed: Disk) -> list[str]:
    """Reject devices that lsblk reports as disks but are not targets."""

    reasons: list[str] = []
    kname = (probed.kname or "").lower()
    if kname.startswith(("fd", "sr", "loop", "ram", "zram")):
        reasons.append("not a hard disk (floppy/optical/loop/ram device)")
    if probed.size_bytes and probed.size_bytes < MIN_TARGET_BYTES:
        reasons.append(
            "disk is too small for an installation target ({} MiB)".format(
                probed.size_bytes // MIB
            )
        )
    return reasons


def _in_use_reasons(probed: Disk) -> list[str]:
    reasons: list[str] = []
    mounts = _mount_sources()
    swaps = _swap_sources()
    mdstat = _mdstat()

    def check_source(source: str, what: str) -> None:
        source = os.path.realpath(source) if source.startswith("/dev/") else source
        if source in mounts:
            reasons.append(f"{what} is mounted on {mounts[source]}")
        if source in swaps:
            reasons.append(f"{what} is in use as swap")

    check_source(probed.path, probed.path)
    for child in probed.children:
        check_source(child.node, child.node)
        if child.mountpoint:
            if child.mountpoint == "[SWAP]":
                reasons.append(f"{child.node} is in use as swap")
            else:
                reasons.append(f"{child.node} is mounted on {child.mountpoint}")

    for kname in [probed.kname, *[os.path.basename(c.node) for c in probed.children]]:
        if not kname:
            continue
        holders = _holders(kname)
        if holders:
            reasons.append(f"{kname} is held by {', '.join(holders)}")
        if kname and kname in mdstat:
            reasons.append(f"{kname} is part of an MD array")

    for child in probed.children:
        ctype = (child.type or "").lower()
        if ctype in ("lvm", "crypt", "raid0", "raid1", "raid4", "raid5", "raid6", "raid10", "dm", "md"):
            reasons.append(f"{child.node} is a {ctype} device")
    return list(dict.fromkeys(reasons))


class Probe:
    def __init__(self, runner: CommandRunner) -> None:
        self.runner = runner
        self._lsblk_cache: tuple[Disk, ...] | None = None
        self._live_kname: str | None = None
        self._live_candidates: tuple[str, ...] = ()

    # ------------------------------------------------------------------
    # lsblk / live media
    # ------------------------------------------------------------------
    def lsblk(self, refresh: bool = False) -> tuple[Disk, ...]:
        if self._lsblk_cache is not None and not refresh:
            return self._lsblk_cache
        result = self.runner.run(
            ("lsblk", "--json", "--bytes", "--output", LSBLK_FIELDS),
            step="probe",
            read_only=True,
            destructive=False,
            description="enumerate block devices",
        )
        self._lsblk_cache = parse_lsblk_json(result.output)
        return self._lsblk_cache

    def _live_candidates_from_system(self) -> list[str]:
        candidates: list[str] = []
        livedev_path = "/run/initramfs/livedev"
        if os.path.islink(livedev_path):
            # dracut may point this at the block device instead of storing
            # its name as text; resolve it without opening it.
            candidates.append(os.path.realpath(livedev_path))
        else:
            livedev = _read_text(livedev_path).strip()
            if livedev:
                candidates.append(livedev)
        try:
            result = self.runner.run(
                ("findmnt", "-n", "-o", "SOURCE", "/run/initramfs/live"),
                step="probe",
                read_only=True,
                destructive=False,
                allow_failure=True,
                description="find the live media mount source",
            )
            if result.ok:
                source = result.output.strip().splitlines()
                if source:
                    candidates.append(source[0])
        except CommandError:
            pass
        try:
            result = self.runner.run(
                ("blkid", "-L", "TENKO"),
                step="probe",
                read_only=True,
                destructive=False,
                allow_failure=True,
                description="find the Tenko ISO by volume label",
            )
            if result.ok and result.output.strip():
                candidates.append(result.output.strip().splitlines()[0])
        except CommandError:
            pass
        return list(dict.fromkeys(c for c in candidates if c))

    def _resolve_live_disk(self, candidates: Sequence[str]) -> str | None:
        disks = self.lsblk(refresh=True)
        for candidate in candidates:
            candidate = candidate.strip()
            if not candidate:
                continue
            real = os.path.realpath(candidate) if candidate.startswith("/dev/") else candidate
            candidate_names = {candidate, real, os.path.basename(candidate), os.path.basename(real)}
            for probed in disks:
                names = {probed.path, os.path.realpath(probed.path), probed.kname}
                if names & candidate_names:
                    return probed.kname
                for child in probed.children:
                    child_real = os.path.realpath(child.node) if child.node.startswith("/dev/") else child.node
                    child_names = {
                        child.node,
                        child_real,
                        os.path.basename(child.node),
                        os.path.basename(child_real),
                    }
                    if child_names & candidate_names:
                        return probed.kname
        return None

    def detect_live_disk(self, refresh: bool = False) -> str | None:
        if self._live_kname is not None and not refresh:
            return self._live_kname
        candidates = self._live_candidates_from_system()
        self._live_candidates = tuple(candidates)
        resolved = self._resolve_live_disk(candidates)
        if resolved is None:
            # CD-ROM (sr*) and loop-mounted ISO media are not "disk" entries
            # in lsblk, but it is still enough to identify them for the
            # safety check: they are never in the selectable whole-disk list.
            for candidate in candidates:
                real = os.path.realpath(candidate) if candidate.startswith("/dev/") else candidate
                if os.path.exists(real):
                    resolved = os.path.basename(real)
                    break
        self._live_kname = resolved
        return self._live_kname

    @property
    def live_candidates(self) -> tuple[str, ...]:
        return self._live_candidates

    # ------------------------------------------------------------------
    # Partition tables
    # ------------------------------------------------------------------
    def _sector_size(self, probed: Disk) -> int:
        try:
            result = self.runner.run(
                ("blockdev", "--getss", probed.path),
                step="probe",
                read_only=True,
                destructive=False,
                allow_failure=True,
                description="read logical sector size",
            )
            value = int((result.output or "").strip() or 0)
            if value > 0:
                return value
        except (CommandError, ValueError):
            pass
        return probed.sector_size or 512

    def _total_sectors(self, probed: Disk, unit: int) -> int | None:
        try:
            result = self.runner.run(
                ("blockdev", "--getsz", probed.path),
                step="probe",
                read_only=True,
                destructive=False,
                allow_failure=True,
                description="read device size in 512-byte sectors",
            )
            getsz = int((result.output or "").strip() or 0)
            if getsz > 0:
                return (getsz * 512) // unit
        except (CommandError, ValueError):
            pass
        if probed.size_bytes:
            return probed.size_bytes // unit
        return None

    def read_table(self, probed: Disk) -> PartitionTable:
        unit = self._sector_size(probed)
        total = self._total_sectors(probed, unit)
        result = self.runner.run(
            ("sfdisk", "--json", probed.path),
            step="probe",
            read_only=True,
            destructive=False,
            allow_failure=True,
            description="read the partition table",
        )
        if not result.ok or not (result.output or "").strip():
            return PartitionTable(
                device=probed.path,
                unit=unit,
                total_sectors=total,
            )
        # Let sfdisk's own sectorsize win if blockdev and sfdisk disagree.
        table = parse_sfdisk_json(
            result.output,
            device=probed.path,
            total_sectors=total,
        )
        if table.unit <= 0:
            table = PartitionTable(
                device=probed.path,
                unit=unit,
                total_sectors=total,
                label=table.label,
                id=table.id,
                firstlba=table.firstlba,
                lastlba=table.lastlba,
                partitions=table.partitions,
            )
        elif table.unit != unit:
            total = self._total_sectors(probed, table.unit)
            table = replace(table, total_sectors=total)
        # sfdisk knows the GPT type and partition GUID but not the filesystem
        # UUID; enrich existing entries from lsblk so an existing ESP can be
        # reused in fstab by UUID.
        children = {child.number: child for child in probed.children}
        enriched = []
        for part in table.partitions:
            child = children.get(part.number)
            if child is not None and (child.fs_uuid or child.fstype):
                part = replace(
                    part,
                    fs_uuid=part.fs_uuid or child.fs_uuid,
                    fstype=part.fstype or child.fstype,
                    label=part.label or child.label,
                )
            enriched.append(part)
        return replace(table, partitions=tuple(enriched))

    def blkid_uuid(self, device: str) -> str | None:
        try:
            result = self.runner.run(
                ("blkid", "-s", "UUID", "-o", "value", device),
                step="probe",
                read_only=True,
                destructive=False,
                allow_failure=True,
                description="read a filesystem UUID",
            )
            value = (result.output or "").strip().splitlines()
            return value[0].strip() if value else None
        except CommandError:
            return None

    # ------------------------------------------------------------------
    # Safety classification
    # ------------------------------------------------------------------
    def probe_disks(self, refresh: bool = False) -> list[ProbedDisk]:
        disks = self.lsblk(refresh=refresh)
        live_kname = self.detect_live_disk(refresh=refresh)
        probed: list[ProbedDisk] = []
        for item in disks:
            live = item.kname == live_kname
            reasons: list[str] = []
            if live:
                reasons.append("installation media")
            if item.ro:
                reasons.append("disk is read-only")
            if item.fstype:
                reasons.append(f"whole-disk filesystem {item.fstype}")
            if item.pttype and item.pttype.lower() not in ("gpt",):
                if item.pttype.lower() in ("dos", "mbr"):
                    reasons.append(
                        "MBR (legacy) partition table; Tenko requires GPT"
                    )
                else:
                    reasons.append(f"unsupported partition table {item.pttype}")
            reasons.extend(_device_class_reasons(item))
            reasons.extend(_in_use_reasons(item))
            table = None
            if not live and not item.ro:
                try:
                    table = self.read_table(item)
                except Exception as exc:  # a broken disk must not kill the UI
                    reasons.append(f"cannot read partition table: {exc}")
            selectable = not reasons
            probed.append(
                ProbedDisk(
                    disk=item,
                    table=table,
                    live=live,
                    selectable=selectable,
                    reasons=tuple(dict.fromkeys(reasons)),
                )
            )
        # A disk that merely contains the live partition is never selectable,
        # even if the live device could not be resolved to the whole disk.
        return probed

    def find_disk(self, path: str, refresh: bool = False) -> ProbedDisk | None:
        for item in self.probe_disks(refresh=refresh):
            if item.disk.path == path or item.disk.kname == path:
                return item
        return None

    # ------------------------------------------------------------------
    # Device readiness
    # ------------------------------------------------------------------
    def wait_for_partuuid(self, plan: disk.LayoutPlan, timeout: float = 15.0) -> bool:
        if self.runner.dry_run:
            return True
        paths = [plan.esp.by_partuuid, plan.root.by_partuuid]
        if plan.swap is not None:
            paths.append(plan.swap.by_partuuid)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if all(os.path.exists(path) for path in paths):
                return True
            time.sleep(0.25)
        return all(os.path.exists(path) for path in paths)

    def wait_for_partuuids(self, layout, timeout: float = 15.0) -> bool:
        """Wait until every planned partition has a by-partuuid link."""

        if self.runner.dry_run:
            return True
        paths = [part.by_partuuid for part in layout.new_partitions]
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if all(os.path.exists(path) for path in paths):
                return True
            time.sleep(0.25)
        return all(os.path.exists(path) for path in paths)

    def resolve_partition(self, part: disk.PlannedPartition) -> str:
        if os.path.exists(part.by_partuuid):
            return part.by_partuuid
        if part.node and os.path.exists(part.node):
            return part.node
        return part.by_partuuid

    # ------------------------------------------------------------------
    # Preflight
    # ------------------------------------------------------------------
    @staticmethod
    def secure_boot_state() -> bool | None:
        """Return True if Secure Boot is on, False if off, None if unknown."""

        directory = "/sys/firmware/efi/efivars"
        try:
            names = [
                name
                for name in os.listdir(directory)
                if name.startswith("SecureBoot-")
            ]
        except OSError:
            return None
        for name in names:
            try:
                with open(os.path.join(directory, name), "rb") as handle:
                    data = handle.read(5)
            except OSError:
                continue
            if len(data) >= 5:
                return data[4] != 0
        return None

    def preflight(
        self,
        *,
        repo: str,
        target: str,
        live_kname: str | None,
        dry_run: bool = False,
    ) -> list[Check]:
        checks: list[Check] = []

        if dry_run:
            checks.append(Check(True, "dry-run", "privileged checks relaxed"))
        else:
            checks.append(
                Check(os.geteuid() == 0, "running as root", f"euid={os.geteuid()}")
            )

        efi = os.path.isdir("/sys/firmware/efi")
        efivars = os.path.ismount("/sys/firmware/efi/efivars")
        if dry_run:
            checks.append(Check(True, "UEFI firmware", "not enforced in dry-run"))
        else:
            checks.append(
                Check(
                    bool(efi and efivars),
                    "UEFI firmware and efivarfs",
                    "/sys/firmware/efi + efivars",
                )
            )

        secure = self.secure_boot_state()
        if dry_run:
            checks.append(
                Check(
                    True,
                    "Secure Boot",
                    "not enforced in dry-run"
                    if secure is None
                    else ("enabled (dry-run only)" if secure else "disabled"),
                )
            )
        elif secure is True:
            checks.append(
                Check(
                    False,
                    "Secure Boot",
                    "Secure Boot is enabled; the Tenko bootloader is "
                    "unsigned, disable Secure Boot in the firmware setup",
                )
            )
        else:
            checks.append(
                Check(
                    True,
                    "Secure Boot",
                    "disabled" if secure is False else "state unknown",
                )
            )

        missing = [
            name for name in REQUIRED_TOOLS if shutil.which(name, path=TOOL_PATH) is None
        ]
        checks.append(
            Check(
                not missing,
                "required tools",
                "missing: " + ", ".join(missing) if missing else "all present",
            )
        )

        repodata = repo.rstrip("/") + "/repodata/repomd.xml" if "://" in repo \
            else os.path.join(repo, "repodata", "repomd.xml")
        repo_ok, repo_detail = _repository_reachable(repodata)
        if dry_run and not repo_ok:
            checks.append(
                Check(True, "package repository", f"{repo} (missing; dry-run only)")
            )
        else:
            checks.append(Check(repo_ok, "package repository", repo_detail))

        if live_kname:
            checks.append(Check(True, "installation media", f"/dev/{live_kname}"))
        else:
            checks.append(
                Check(
                    False,
                    "installation media",
                    "cannot identify the live medium from /run/initramfs/livedev, "
                    "the /run/initramfs/live mount, or the TENKO label",
                )
            )

        if dry_run:
            checks.append(Check(True, "install target", f"{target} (dry-run)"))
        else:
            target_mounted = os.path.ismount(target)
            checks.append(
                Check(
                    not target_mounted,
                    "install target is free",
                    f"{target} is already a mountpoint" if target_mounted else target,
                )
            )

        try:
            os.makedirs("/run/tenko", exist_ok=True)
            writable = os.access("/run/tenko", os.W_OK)
        except OSError:
            writable = False
        checks.append(Check(writable, "log directory", "/run/tenko"))
        return checks
