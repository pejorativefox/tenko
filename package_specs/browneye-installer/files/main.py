"""Command line entry point and screen flow for browneye-installer."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict
from typing import Any, Sequence

import curses

import disk
import layout as layout_module
import simulate as simulate_module
from disk import Disk, PartitionTable, Region
from install import (
    ConfigError,
    InstallConfig,
    InstallError,
    Installer,
    PACKAGE_SETS,
)
from layout import (
    DiskSpec,
    InstallLayout,
    InstallSpec,
    PartitionSpec,
)
from log import Logger
from probe import Check, Probe, ProbedDisk
from runner import CommandError, CommandRunner
from ui import BACK, QUIT, RESCAN, CursesUI, Field, Row

VERSION = "13.1"
DEFAULT_REPO = "https://repo.pjfox.xyz/packages/13.1/"
DEFAULT_TARGET = "/mnt/browneye"
LOG_DIR = "/run/browneye"
LOG_JSONL = os.path.join(LOG_DIR, "install.jsonl")
PLAN_JSON = os.path.join(LOG_DIR, "plan.json")
ANSWER_PATHS = (
    "/run/initramfs/live/answer.json",
    "/sys/firmware/qemu_fw_cfg/by_name/opt/browneye/answer.json/raw",
    "/dev/disk/by-label/BROWNEYE-ANSWER/answer.json",
)
MIB = 1024 * 1024
GIB = 1024 * MIB


# ---------------------------------------------------------------------------
# Console / serial mirroring
# ---------------------------------------------------------------------------


def serial_write(text: str) -> None:
    for path in ("/dev/ttyS0", "/dev/ttyS1"):
        try:
            fd = os.open(path, os.O_WRONLY | os.O_NOCTTY | os.O_NONBLOCK)
        except OSError:
            continue
        try:
            os.write(fd, (text + "\r\n").encode("utf-8", "replace"))
        except OSError:
            pass
        finally:
            os.close(fd)


def console_line(line: str) -> None:
    print(line, flush=True)
    serial_write(line)


def marker(text: str) -> None:
    line = "BROWNEY-INSTALL: " + text
    print(line, flush=True)
    serial_write(line)


def _write_plan_json(plan: InstallLayout, config: InstallConfig) -> None:
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        payload = {
            "version": 2,
            "installer": VERSION,
            "config": config.public_dict(),
            "plan": plan.to_dict(),
        }
        with open(PLAN_JSON, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except OSError:
        pass


def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def write_probe_snapshot(
    probe: Probe,
    probed: ProbedDisk | Sequence[ProbedDisk],
    logger: Logger,
) -> None:
    """Write /run/browneye/probe.json for post-mortem debugging."""

    probed_list = [probed] if isinstance(probed, ProbedDisk) else list(probed)
    dmi = {}
    for name in (
        "sys_vendor",
        "product_name",
        "product_version",
        "product_serial",
        "board_vendor",
        "board_name",
        "bios_vendor",
        "bios_version",
        "bios_date",
    ):
        value = _read_file("/sys/class/dmi/id/" + name).strip()
        if value:
            dmi[name] = value
    uname = os.uname()
    data: dict[str, Any] = {
        "installer": VERSION,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cmdline": _read_file("/proc/cmdline").strip(),
        "uname": {
            "sysname": uname.sysname,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
        },
        "os_release": _read_file("/etc/os-release"),
        "dmi": dmi,
        "meminfo": _read_file("/proc/meminfo"),
        "mounts": _read_file("/proc/mounts"),
        "swaps": _read_file("/proc/swaps"),
        "mdstat": _read_file("/proc/mdstat"),
        "simulated": bool(getattr(probe, "simulated", False)),
        "secure_boot": probe.secure_boot_state(),
        "disks": [
            {
                "path": item.disk.path,
                "kname": item.disk.kname,
                "model": item.disk.model,
                "serial": item.disk.serial,
                "size_bytes": item.disk.size_bytes,
                "sector_size": item.disk.sector_size,
                "pttype": item.disk.pttype,
                "live": item.live,
                "selectable": item.selectable,
                "reasons": list(item.reasons),
                "table": asdict(item.table) if item.table is not None else None,
            }
            for item in probed_list
        ],
    }
    if probed_list:
        data["disk"] = data["disks"][0]
    if not getattr(probe, "simulated", False):
        for label, argv in (
            ("lsblk", ("lsblk", "--json", "--bytes")),
            ("findmnt", ("findmnt", "-J")),
            ("efibootmgr", ("efibootmgr", "-v")),
        ):
            try:
                result = probe.runner.run(
                    argv,
                    step="probe",
                    read_only=True,
                    destructive=False,
                    allow_failure=True,
                    description="snapshot " + label,
                )
                data[label] = result.output
            except Exception as exc:
                data[label] = "unavailable: {}".format(exc)
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(os.path.join(LOG_DIR, "probe.json"), "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True, default=str)
            handle.write("\n")
    except OSError as exc:
        logger.warning("probe-snapshot-failed", error=str(exc))


# ---------------------------------------------------------------------------
# Arguments and answer files
# ---------------------------------------------------------------------------

_CMDLINE = {
    "answer": None,
    "auto": False,
    "serial": False,
    "dry_run": False,
    "debug": False,
}


def read_cmdline() -> dict[str, Any]:
    result = dict(_CMDLINE)
    try:
        with open("/proc/cmdline", "r", encoding="utf-8", errors="replace") as handle:
            tokens = handle.read().split()
    except OSError:
        return result
    for token in tokens:
        if token.startswith("browneye.answer="):
            result["answer"] = token.split("=", 1)[1]
        elif token in ("browneye.auto=1", "browneye.auto=true"):
            result["auto"] = True
        elif token in ("browneye.console=serial", "browneye.serial=1"):
            result["serial"] = True
        elif token in ("browneye.dry_run=1", "browneye.dry-run=1"):
            result["dry_run"] = True
        elif token in ("browneye.debug=1", "browneye.debug=true"):
            result["debug"] = True
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="browneye-installer",
        description="Install Browneye Linux 13.1 on a GPT disk.",
    )
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument(
        "--repo",
        default=None,
        help="RPM repository, URL or path (default: the Browneye 13.1 repository)",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="installation mount point (default: /mnt/browneye)",
    )
    parser.add_argument("--answer", default=None, help="JSON answer file")
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="run from an answer file; no curses; serial markers",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="line-oriented fallback for serial consoles",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="plan and log every command without executing mutating commands",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="use synthetic disks and force dry-run (no root or live media)",
    )
    parser.add_argument(
        "--simulate-scenario",
        choices=simulate_module.SCENARIOS,
        default=None,
        help="synthetic disk scenario (implies --simulate)",
    )
    parser.add_argument(
        "--plan-json",
        action="store_true",
        help="print the validated layout plan as JSON and exit",
    )
    parser.add_argument(
        "--reboot",
        action="store_true",
        help="reboot after a successful non-interactive install",
    )
    parser.add_argument(
        "--no-reboot",
        action="store_true",
        help="never reboot automatically",
    )
    parser.add_argument("--debug", action="store_true", help="verbose logging")
    args = parser.parse_args(argv)

    if args.simulate_scenario:
        args.simulate = True
    if args.simulate:
        args.dry_run = True

    cmd = read_cmdline()
    if args.answer is None:
        args.answer = cmd["answer"]
    if not args.non_interactive and cmd["auto"]:
        args.non_interactive = True
    if not args.plain and cmd["serial"]:
        args.plain = True
    if not args.dry_run and cmd["dry_run"]:
        args.dry_run = True
    if not args.debug and cmd["debug"]:
        args.debug = True
    if args.repo is None:
        args.repo = DEFAULT_REPO
    if args.target is None:
        args.target = DEFAULT_TARGET
    return args


ANSWER_LABEL = "/dev/disk/by-label/BROWNEYE-ANSWER"
ANSWER_MOUNT = "/run/browneye/answer"


def mount_answer_disk() -> str | None:
    """Mount a BROWNEYE-ANSWER medium read-only and return its answer.json.

    /dev/disk/by-label/X is a symlink to a block device, not a directory, so
    the medium has to be mounted before the answer file can be read.
    """
    if not os.path.exists(ANSWER_LABEL):
        return None
    try:
        os.makedirs(ANSWER_MOUNT, exist_ok=True)
        if not os.path.ismount(ANSWER_MOUNT):
            subprocess.run(
                ("mount", "-o", "ro", ANSWER_LABEL, ANSWER_MOUNT),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=15, check=False,
            )
    except (OSError, subprocess.SubprocessError):
        return None
    path = os.path.join(ANSWER_MOUNT, "answer.json")
    return path if os.path.isfile(path) else None


def find_answer_path(explicit: str | None, timeout: float = 15.0) -> str | None:
    """Locate the answer file, waiting briefly for udev/block devices.

    The live system starts the installer as soon as multi-user is reached;
    a USB or virtio answer disk may not have its /dev/disk/by-label link yet.
    """
    deadline = time.monotonic() + max(0.0, timeout)
    while True:
        candidates = [explicit] if explicit else list(ANSWER_PATHS)
        for path in candidates:
            if path and os.path.isfile(path):
                return path
        if explicit is None:
            mounted = mount_answer_disk()
            if mounted:
                return mounted
        if time.monotonic() >= deadline:
            return None
        time.sleep(0.5)


def load_answer(path: str) -> dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise ConfigError(f"cannot read answer file {path}: {exc}") from exc
    except ValueError as exc:
        raise ConfigError(f"answer file {path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError("answer file must contain a JSON object")
    return data


# ---------------------------------------------------------------------------
# Preflight and planning
# ---------------------------------------------------------------------------


def run_preflight(
    probe: Probe,
    config: InstallConfig,
    logger: Logger,
) -> tuple[list[Check], bool]:
    live_kname = probe.detect_live_disk(refresh=True)
    checks = probe.preflight(
        repo=config.repo,
        target=config.target,
        live_kname=live_kname,
        dry_run=config.dry_run,
    )
    for check in checks:
        if check.ok:
            logger.info(
                "preflight-ok",
                label=check.label,
                detail=check.detail,
            )
        else:
            logger.error(
                "preflight-failed",
                label=check.label,
                detail=check.detail,
            )
    return checks, all(check.ok for check in checks)


def _disk_matches(probed: ProbedDisk, spec: DiskSpec) -> list[str]:
    issues: list[str] = []
    if spec.serial:
        if not probed.disk.serial:
            issues.append("the layout requires a serial but the disk has none")
        elif spec.serial.casefold() != probed.disk.serial.casefold():
            issues.append(
                "disk serial changed: {} != {}".format(
                    probed.disk.serial, spec.serial
                )
            )
    if spec.size_bytes is not None and probed.disk.size_bytes != spec.size_bytes:
        issues.append(
            "disk size changed: {} != {}".format(
                probed.disk.size_bytes, spec.size_bytes
            )
        )
    if not spec.serial and spec.model and probed.disk.model:
        if spec.model.strip().casefold() != probed.disk.model.strip().casefold():
            issues.append(
                "disk model changed: {} != {}".format(
                    probed.disk.model, spec.model
                )
            )
    return issues


def build_layout(
    probe: Probe,
    config: InstallConfig,
) -> tuple[InstallLayout, list[ProbedDisk], dict[str, list[Region]]]:
    """Probe every disk in the layout and build the validated plan."""

    probed_disks: list[ProbedDisk] = []
    tables: dict[str, PartitionTable] = {}
    totals: dict[str, int | None] = {}
    regions_by_disk: dict[str, list[Region]] = {}
    for spec in config.layout.disks:
        probed = probe.find_disk(spec.path, refresh=True)
        if probed is None:
            raise ConfigError("disk {} was not found".format(spec.path))
        if probed.live:
            raise ConfigError(
                "disk {} is the live installation media".format(spec.path)
            )
        if not probed.selectable:
            raise ConfigError(
                "disk {} is not selectable: {}".format(
                    spec.path, "; ".join(probed.reasons) or "unknown reason"
                )
            )
        issues = _disk_matches(probed, spec)
        if issues:
            raise ConfigError("; ".join(issues))
        table = probed.table or probe.read_table(probed.disk)
        tables[spec.path] = table
        totals[spec.path] = table.total_sectors
        probed_disks.append(probed)
        remaining = table.without(spec.delete_partitions)
        regions_by_disk[spec.path] = disk.find_free_regions(
            remaining,
            total_sectors=table.total_sectors,
            unit=table.unit,
            align=max(1, MIB // (table.unit or 512)),
        )
    try:
        plan = layout_module.plan_install(
            tables,
            config.layout,
            total_sectors=totals,
        )
    except disk.PlanError as exc:
        raise ConfigError(str(exc)) from exc
    for item in plan.disks:
        for warning in item.warnings:
            config_warning = "{}: {}".format(item.disk_path, warning)
            if config_warning not in config.warnings:
                config.warnings.append(config_warning)
    return plan, probed_disks, regions_by_disk


# ---------------------------------------------------------------------------
# Shared install runner
# ---------------------------------------------------------------------------


def execute_install(
    config: InstallConfig,
    plan: InstallLayout,
    probe: Probe,
    runner: CommandRunner,
    logger: Logger,
    *,
    on_step=None,
    on_line=None,
) -> None:
    _write_plan_json(plan, config)
    installer = Installer(
        config,
        runner,
        logger,
        probe,
        plan,
        on_step=on_step,
        on_line=on_line,
    )
    installer.run()


# ---------------------------------------------------------------------------
# Non-interactive mode
# ---------------------------------------------------------------------------


def run_noninteractive(
    args: argparse.Namespace,
    logger: Logger,
    runner: CommandRunner,
    probe: Probe,
) -> int:
    answer_path = find_answer_path(args.answer)
    if not answer_path:
        marker("FAIL answer: no answer file found")
        return 2
    try:
        data = load_answer(answer_path)
        config = InstallConfig.from_mapping(
            data,
            repo=args.repo,
            target=args.target,
            dry_run=args.dry_run,
        )
    except ConfigError as exc:
        marker("FAIL answer: " + str(exc))
        return 2
    issues = config.validate()
    if issues:
        marker("FAIL answer: " + "; ".join(issues))
        return 2

    # The answer file may request a dry run even when the command line did
    # not.  Make the runner agree before any command is considered.
    if config.dry_run and not runner.dry_run:
        runner.dry_run = True
        logger.info("dry-run-enabled-by-answer")

    logger.info("answer-file", path=answer_path, config=config.public_dict())
    checks, ok = run_preflight(probe, config, logger)
    if not ok:
        failing = "; ".join(
            "{}: {}".format(check.label, check.detail)
            for check in checks
            if not check.ok
        )
        marker("FAIL preflight: " + failing)
        return 2

    try:
        plan, probed, _regions = build_layout(probe, config)
    except (ConfigError, disk.PlanError) as exc:
        marker("FAIL plan: " + str(exc))
        return 2
    write_probe_snapshot(probe, probed, logger)
    _write_plan_json(plan, config)
    if args.plan_json:
        print(json.dumps(plan.to_dict(), indent=2, sort_keys=True))
        return 0

    def on_step(index: int, total: int, title: str) -> None:
        marker("STEP {} {}".format(index, title))

    try:
        execute_install(
            config,
            plan,
            probe,
            runner,
            logger,
            on_step=on_step,
            on_line=console_line,
        )
    except InstallError as exc:
        marker("FAIL {}: {}".format(exc.step, exc.message))
        return 1
    except (CommandError, OSError, RuntimeError) as exc:
        marker("FAIL install: " + str(exc))
        return 1

    if config.dry_run:
        marker("OK (dry-run)")
        return 0
    marker("OK")
    if args.reboot and not args.no_reboot:
        try:
            runner.run(("reboot",), step="finish", description="reboot after install")
        except CommandError:
            pass
    return 0


# ---------------------------------------------------------------------------
# Plain / serial mode
# ---------------------------------------------------------------------------


def _ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        value = input(prompt + suffix + ": ").strip()
    except EOFError:
        return default
    return value or default


def _existing_esp(table: PartitionTable) -> disk.Partition | None:
    for part in table.partitions:
        if (part.type or "").upper() == disk.ESP_TYPE:
            return part
    return None


def _prompt_delete(table: PartitionTable) -> tuple[int, ...]:
    print("\nCurrent partitions:")
    for part in table.partitions:
        print(
            "  {}  start={} MiB  size={} MiB  {}  {}".format(
                part.number,
                (part.start * table.unit) // MIB,
                (part.size * table.unit) // MIB,
                disk.type_name(part.type, table.is_mbr),
                part.name or "",
            )
        )
    text = _ask("Delete partition numbers (comma-separated, blank = none)", "")
    deleted: list[int] = []
    for token in text.replace(" ", "").split(","):
        if not token:
            continue
        try:
            deleted.append(int(token))
        except ValueError as exc:
            raise ValueError("delete list is not a list of numbers") from exc
    return tuple(deleted)


def _default_root_partitions(
    table: PartitionTable,
    root_fstype: str,
    root_mib: int | None,
    swap_mib: int,
) -> list[PartitionSpec]:
    specs: list[PartitionSpec] = []
    esp = _existing_esp(table)
    if esp is not None:
        specs.append(
            PartitionSpec(
                role="esp",
                fstype="vfat",
                mountpoint="/boot",
                existing_number=esp.number,
                format=False,
            )
        )
    else:
        specs.append(
            PartitionSpec(
                role="esp",
                fstype="vfat",
                mountpoint="/boot",
                size_mib=layout_module.ESP_MIB,
            )
        )
    if swap_mib > 0:
        specs.append(
            PartitionSpec(
                role="swap",
                fstype="swap",
                size_mib=swap_mib,
            )
        )
    specs.append(
        PartitionSpec(
            role="root",
            fstype=root_fstype,
            mountpoint="/",
            size_mib=root_mib,
        )
    )
    return specs


def run_plain(
    args: argparse.Namespace,
    logger: Logger,
    runner: CommandRunner,
    probe: Probe,
) -> int:
    answer_path = find_answer_path(args.answer)
    if answer_path:
        return run_noninteractive(args, logger, runner, probe)

    logger.console = console_line
    empty_spec = InstallSpec(disks=())
    preflight_config = InstallConfig(
        layout=empty_spec,
        repo=args.repo,
        target=args.target,
        dry_run=args.dry_run,
    )
    checks, ok = run_preflight(probe, preflight_config, logger)
    for check in checks:
        print("  [{}] {}: {}".format("ok" if check.ok else "!!", check.label, check.detail))
    if not ok:
        marker("FAIL preflight")
        return 2

    probed = probe.probe_disks(refresh=True)
    selectable = [item for item in probed if item.selectable]
    if not selectable:
        print("No selectable disks.")
        for item in probed:
            print("  {}: {}".format(item.disk.path, "; ".join(item.reasons)))
        return 2
    print("Select disks (first one becomes the root disk):")
    for index, item in enumerate(selectable, 1):
        print(
            "  {}. {}  {}  {}  {}".format(
                index,
                item.disk.path,
                disk.human_size(item.disk.size_bytes),
                item.disk.pttype or "blank",
                item.disk.model or "",
            )
        )
    choice = _ask("Disk numbers (comma-separated)", "1")
    selected: list[ProbedDisk] = []
    try:
        for token in choice.replace(" ", "").split(","):
            if token:
                selected.append(selectable[int(token) - 1])
    except (ValueError, IndexError):
        marker("FAIL disk selection")
        return 2
    if not selected:
        marker("FAIL disk selection")
        return 2

    disk_specs: list[DiskSpec] = []
    try:
        for position, item in enumerate(selected):
            table = item.table or probe.read_table(item.disk)
            deleted = _prompt_delete(table)
            parts: list[PartitionSpec] = []
            if position == 0:
                root_fstype = _ask("Root filesystem (ext4/btrfs)", "ext4")
                if root_fstype not in ("ext4", "btrfs"):
                    marker("FAIL root filesystem")
                    return 2
                root_text = _ask("Root size MiB (blank = fill region)", "")
                swap_text = _ask("Swap size MiB (0 = none)", "2048")
                root_mib = int(root_text) if root_text else None
                swap_mib = int(swap_text) if swap_text else 0
                parts = _default_root_partitions(
                    table, root_fstype, root_mib, swap_mib
                )
            else:
                mountpoint = _ask(
                    "{} mount point (blank = do not use this disk)".format(
                        item.disk.path
                    ),
                    "",
                )
                if mountpoint:
                    fstype = _ask("Filesystem (ext4/btrfs/vfat)", "ext4")
                    size_text = _ask("Size MiB (blank = fill region)", "")
                    parts.append(
                        PartitionSpec(
                            role="data",
                            fstype=fstype,
                            mountpoint=mountpoint,
                            size_mib=int(size_text) if size_text else None,
                        )
                    )
            disk_specs.append(
                DiskSpec(
                    path=item.disk.path,
                    serial=item.disk.serial,
                    size_bytes=item.disk.size_bytes,
                    model=item.disk.model,
                    delete_partitions=deleted,
                    partitions=tuple(parts),
                )
            )
    except ValueError as exc:
        marker("FAIL input: " + str(exc))
        return 2

    hostname = _ask("Hostname", "browneye")
    admin = _ask("Admin user", "admin")
    try:
        password = getpass.getpass("Admin password: ")
        confirm_password = getpass.getpass("Confirm password: ")
    except EOFError:
        marker("FAIL password")
        return 2
    if password != confirm_password or not password:
        marker("FAIL password: passwords do not match or are empty")
        return 2
    package_set = _ask("Package set (desktop/base)", "desktop")
    spec = InstallSpec(disks=tuple(disk_specs))
    config = InstallConfig(
        layout=spec,
        package_set=package_set if package_set in PACKAGE_SETS else "desktop",
        hostname=hostname,
        admin_user=admin,
        admin_password=password,
        confirm_disk=selected[0].disk.path,
        confirm_phrase="ERASE",
        repo=args.repo,
        target=args.target,
        dry_run=args.dry_run,
    )
    issues = config.validate()
    if issues:
        print("Configuration errors: " + "; ".join(issues))
        return 2
    try:
        plan, probed_used, _regions = build_layout(probe, config)
    except (ConfigError, disk.PlanError) as exc:
        marker("FAIL plan: " + str(exc))
        return 2
    write_probe_snapshot(probe, probed_used, logger)
    print("\nPlan:")
    for line in layout_module.describe_layout(plan):
        print("  " + line)
    for warning in config.warnings:
        print("  warning: " + warning)
    print("\nThere is no undo after formatting begins.")
    typed_disk = _ask("Type the root disk path to confirm", "")
    typed_phrase = _ask("Type ERASE to start", "")
    if typed_disk != config.root_disk_path or typed_phrase != "ERASE":
        marker("FAIL confirmation")
        return 2
    config.confirm_disk = typed_disk
    config.confirm_phrase = typed_phrase
    try:
        execute_install(
            config,
            plan,
            probe,
            runner,
            logger,
            on_step=lambda index, total, title: print("[{}/{}] {}".format(index, total, title)),
            on_line=console_line,
        )
    except InstallError as exc:
        marker("FAIL {}: {}".format(exc.step, exc.message))
        return 1
    marker("OK" if not config.dry_run else "OK (dry-run)")
    return 0


# ---------------------------------------------------------------------------
# Curses mode
# ---------------------------------------------------------------------------


def _size_columns(disk_obj: Disk) -> str:
    return disk.human_size(disk_obj.size_bytes)


def _table_label(probed: ProbedDisk) -> str:
    if probed.live:
        return "live"
    if probed.disk.pttype:
        return probed.disk.pttype.upper()
    return "blank"


def _initial_config(args: argparse.Namespace) -> InstallConfig:
    return InstallConfig(
        layout=InstallSpec(disks=()),
        repo=args.repo,
        target=args.target,
        dry_run=args.dry_run,
    )


def _fs_for_existing(part: disk.Partition) -> str:
    fstype = (part.fstype or "").lower()
    if fstype in ("fat", "fat32", "msdos"):
        return "vfat"
    return fstype


def _role_for(mountpoint: str, fstype: str) -> str:
    if fstype == "swap":
        return "swap"
    if mountpoint == "/":
        return "root"
    if mountpoint == "/boot":
        return "esp"
    if not mountpoint:
        return "swap"
    return "data"


def _default_disk_spec(item: ProbedDisk, *, root_disk: bool) -> DiskSpec:
    base = dict(
        path=item.disk.path,
        serial=item.disk.serial,
        size_bytes=item.disk.size_bytes,
        model=item.disk.model,
    )
    if not root_disk:
        return DiskSpec(**base)
    table = item.table or PartitionTable()
    specs: list[PartitionSpec] = []
    esp = _existing_esp(table)
    if esp is not None:
        specs.append(
            PartitionSpec(
                role="esp",
                fstype="vfat",
                mountpoint="/boot",
                existing_number=esp.number,
                format=False,
            )
        )
    else:
        specs.append(
            PartitionSpec(
                role="esp",
                fstype="vfat",
                mountpoint="/boot",
                size_mib=layout_module.ESP_MIB,
            )
        )
    specs.append(
        PartitionSpec(
            role="swap",
            fstype="swap",
            size_mib=layout_module.SWAP_MIB,
        )
    )
    specs.append(
        PartitionSpec(
            role="root",
            fstype="ext4",
            mountpoint="/",
        )
    )
    return DiskSpec(partitions=tuple(specs), **base)


def _select_disks(
    ui: CursesUI, probed: Sequence[ProbedDisk]
) -> list[ProbedDisk] | None:
    selected: set[str] = set()
    while True:
        rows: list[Row] = []
        for item in probed:
            status = "selectable" if item.selectable else "; ".join(item.reasons)
            rows.append(
                Row(
                    "{:<12} {:>8}  {:<8} {:<28} {}".format(
                        item.disk.path,
                        _size_columns(item.disk),
                        _table_label(item),
                        (item.disk.model or "")[:28],
                        status,
                    ),
                    enabled=item.selectable,
                    marker="[x]" if item.disk.path in selected else "[ ]",
                )
            )
        rows.append(Row("Continue with these disks"))
        choice = ui.menu(
            "Select installation disks",
            "The topmost selected disk becomes the root disk. Press Enter "
            "to toggle a disk or to continue.",
            rows,
            footer="Up/Down select   Enter toggle/continue   r rescan   q quit",
            allow_back=True,
        )
        if choice in (QUIT, BACK):
            return None
        if choice == RESCAN:
            return []
        if choice == len(rows) - 1:
            chosen = [
                item for item in probed if item.disk.path in selected
            ]
            if not chosen:
                ui.message(
                    "No disk selected",
                    ["Select at least one disk with Enter."],
                    footer="Press any key to continue",
                )
                continue
            return chosen
        item = probed[choice]
        if not item.selectable:
            continue
        if item.disk.path in selected:
            selected.remove(item.disk.path)
        else:
            selected.add(item.disk.path)


def _existing_row(part: disk.Partition, table: PartitionTable) -> str:
    text = "{}  start {} MiB  size {} MiB  {}".format(
        part.number,
        (part.start * table.unit) // MIB,
        (part.size * table.unit) // MIB,
        disk.type_name(part.type, table.is_mbr),
    )
    if part.fstype:
        text += "  " + part.fstype
    if part.name:
        text += "  " + part.name
    return text


def _add_partition_form(ui: CursesUI) -> PartitionSpec | None:
    values = ui.form(
        "New partition",
        [
            Field("Mount point (blank = swap)", ""),
            Field("Filesystem (ext4/btrfs/vfat/swap)", "ext4"),
            Field("Size MiB (blank = fill region)", ""),
            Field("Region start MiB (blank = auto)", ""),
            Field("Name (optional)", ""),
        ],
        subtitle="A mount point of / makes the partition root; /boot makes it the ESP.",
        footer="Tab next   Enter continue   Esc back",
    )
    if values is None:
        return None
    mount, fstype, size_text, region_text, name = [
        value.strip() for value in values
    ]
    if not mount and fstype != "swap":
        ui.message(
            "Mount point required",
            ["A mount point is required unless the filesystem is swap."],
            footer="Press any key to retry",
        )
        return None
    role = _role_for(mount, fstype)
    if role == "esp":
        fstype = "vfat"
        mount = "/boot"
    elif role == "swap":
        fstype = "swap"
        mount = ""
    try:
        spec = PartitionSpec(
            role=role,
            fstype=fstype,
            mountpoint=mount or None,
            size_mib=int(size_text) if size_text else None,
            region_start_mib=int(region_text) if region_text else None,
            name=name or None,
        )
    except ValueError:
        ui.message(
            "Invalid partition",
            ["Sizes and region starts must be integers."],
            footer="Press any key to retry",
        )
        return None
    issues = spec.validate()
    if issues:
        ui.message("Invalid partition", issues, footer="Press any key to retry")
        return None
    return spec


def _assign_existing_form(
    ui: CursesUI, table: PartitionTable
) -> PartitionSpec | None:
    values = ui.form(
        "Assign an existing partition",
        [
            Field("Partition number", ""),
            Field("Mount point (blank = use as swap)", ""),
            Field("Format it? (y/N)", "n"),
            Field("Filesystem when formatting (blank = keep)", ""),
        ],
        subtitle="Leave format off to keep the existing data and filesystem.",
        footer="Tab next   Enter continue   Esc back",
    )
    if values is None:
        return None
    number_text, mountpoint, format_text, fstype_text = [
        value.strip() for value in values
    ]
    try:
        number = int(number_text)
    except ValueError:
        ui.message(
            "Invalid number",
            ["The partition number must be an integer."],
            footer="Press any key to retry",
        )
        return None
    part = table.find_number(number)
    if part is None:
        ui.message(
            "No such partition",
            ["Partition {} does not exist.".format(number)],
            footer="Press any key to retry",
        )
        return None
    format_existing = format_text.lower() in ("y", "yes")
    detected = _fs_for_existing(part)
    fstype = fstype_text.lower() or detected
    if not format_existing:
        if not detected:
            ui.message(
                "Unknown filesystem",
                [
                    "Partition {} has no readable filesystem.".format(number),
                    "Enable formatting or create a new partition instead.",
                ],
                footer="Press any key to retry",
            )
            return None
        fstype = detected
    if not mountpoint and fstype != "swap":
        ui.message(
            "Mount point required",
            [
                "Partition {} is not swap; enter a mount point.".format(number)
            ],
            footer="Press any key to retry",
        )
        return None
    role = _role_for(mountpoint, fstype)
    if role == "esp":
        fstype = "vfat"
    if role == "swap":
        fstype = "swap"
    elif fstype not in layout_module.DATA_FSTYPES:
        ui.message(
            "Invalid filesystem",
            ["Choose ext4, btrfs or vfat (or swap for no mount point)."],
            footer="Press any key to retry",
        )
        return None
    spec = PartitionSpec(
        role=role,
        fstype=fstype,
        mountpoint=mountpoint or None,
        existing_number=number,
        format=format_existing,
    )
    issues = spec.validate()
    if issues:
        ui.message("Invalid assignment", issues, footer="Press any key to retry")
        return None
    return spec


def _edit_disk(
    ui: CursesUI,
    probe: Probe,
    item: ProbedDisk,
    initial: DiskSpec,
    *,
    root_disk: bool,
) -> DiskSpec | None:
    table = item.table or probe.read_table(item.disk)
    specs = list(initial.partitions)
    delete_set = set(initial.delete_partitions)

    def adopted(number: int) -> PartitionSpec | None:
        return next(
            (spec for spec in specs if spec.existing_number == number), None
        )

    while True:
        rows: list[Row] = []
        for part in sorted(table.partitions, key=lambda value: value.number):
            assigned = adopted(part.number)
            if part.number in delete_set:
                marker, note = "[x]", "delete"
            elif assigned is not None:
                marker = "[+]"
                note = "{}{}{}".format(
                    assigned.role,
                    " " + assigned.mountpoint if assigned.mountpoint else "",
                    " (reformat)" if assigned.format else " (keep)",
                )
            else:
                marker, note = "[ ]", "preserve"
            rows.append(
                Row(_existing_row(part, table), marker=marker, note=note)
            )
        for spec in specs:
            if spec.existing_number is not None:
                continue
            rows.append(
                Row(
                    "NEW {}  {} MiB".format(
                        spec.role,
                        spec.size_mib if spec.size_mib is not None else "fill",
                    ),
                    marker="[+]",
                    note="{} {}".format(
                        spec.fstype, spec.mountpoint or "swap"
                    ),
                )
            )
        actions = len(rows)
        rows.extend(
            [
                Row("Add a new partition"),
                Row("Assign an existing partition"),
                Row("Toggle delete for an existing partition"),
                Row("Remove a planned or assigned partition"),
                Row("Done with this disk"),
            ]
        )
        remaining = table.without(delete_set)
        regions = disk.find_free_regions(
            remaining,
            total_sectors=table.total_sectors,
            unit=table.unit,
            align=max(1, MIB // (table.unit or 512)),
        )
        free_text = ", ".join(
            "{}..{}".format(region.start_mib, region.end_mib)
            for region in regions
        )
        subtitle = "{}  {}  {}{}  free: {}".format(
            disk.human_size(item.disk.size_bytes),
            (table.label or "blank").upper(),
            item.disk.model or "",
            "  (root disk)" if root_disk else "",
            free_text or "none",
        )
        choice = ui.menu(
            "Partition layout - {}".format(item.disk.path),
            subtitle,
            rows,
            footer="Up/Down select   Enter act/continue   r rescan   Esc back",
            allow_back=True,
        )
        if choice in (BACK, QUIT):
            return None
        if choice == RESCAN:
            refreshed = probe.find_disk(item.disk.path, refresh=True) or item
            item = refreshed
            table = refreshed.table or probe.read_table(refreshed.disk)
            continue
        action = choice - actions
        if action == 0:
            spec = _add_partition_form(ui)
            if spec is not None:
                if spec.role in ("root", "esp") and any(
                    existing.role == spec.role for existing in specs
                ):
                    ui.message(
                        "Role already assigned",
                        [
                            "This disk already has a {} partition.".format(
                                spec.role
                            )
                        ],
                        footer="Press any key to retry",
                    )
                    continue
                specs.append(spec)
        elif action == 1:
            spec = _assign_existing_form(ui, table)
            if spec is not None:
                if spec.role in ("root", "esp") and any(
                    existing.role == spec.role
                    for existing in specs
                    if existing.existing_number != spec.existing_number
                ):
                    ui.message(
                        "Role already assigned",
                        [
                            "This disk already has a {} partition.".format(
                                spec.role
                            )
                        ],
                        footer="Press any key to retry",
                    )
                    continue
                number = int(spec.existing_number or 0)
                delete_set.discard(number)
                specs = [
                    existing
                    for existing in specs
                    if existing.existing_number != number
                ]
                specs.append(spec)
        elif action == 2:
            values = ui.form(
                "Delete an existing partition",
                [Field("Partition number", "")],
                subtitle="The partition entry is removed when the plan is applied.",
                footer="Tab next   Enter continue   Esc back",
            )
            if values is None:
                continue
            try:
                number = int(values[0].strip())
            except ValueError:
                continue
            part = table.find_number(number)
            if part is None:
                ui.message(
                    "No such partition",
                    ["Partition {} does not exist.".format(number)],
                    footer="Press any key to retry",
                )
                continue
            specs = [
                spec
                for spec in specs
                if spec.existing_number != number
            ]
            if number in delete_set:
                delete_set.remove(number)
            else:
                delete_set.add(number)
        elif action == 3:
            if not specs:
                ui.message(
                    "Nothing to remove",
                    ["No planned or assigned partition on this disk."],
                    footer="Press any key to retry",
                )
                continue
            remove_rows = [
                Row(
                    "{}{}  {}  {}".format(
                        spec.role,
                        " " + spec.mountpoint if spec.mountpoint else "",
                        spec.fstype,
                        "existing " + str(spec.existing_number)
                        if spec.existing_number is not None
                        else (
                            str(spec.size_mib) + " MiB"
                            if spec.size_mib is not None
                            else "fill"
                        ),
                    )
                )
                for spec in specs
            ]
            picked = ui.menu(
                "Remove a partition",
                "Removing a planned partition does not delete anything on disk.",
                remove_rows,
                footer="Up/Down select   Enter remove   Esc back",
                allow_back=True,
            )
            if picked in (BACK, QUIT):
                continue
            specs.pop(picked)
        elif action == 4:
            candidate = DiskSpec(
                path=item.disk.path,
                serial=item.disk.serial,
                size_bytes=item.disk.size_bytes,
                model=item.disk.model,
                delete_partitions=tuple(sorted(delete_set)),
                partitions=tuple(specs),
            )
            issues = candidate.validate()
            if issues:
                ui.message(
                    "Invalid disk layout", issues, footer="Press any key to retry"
                )
                continue
            try:
                layout_module.plan_disk(
                    table,
                    candidate,
                    disk_path=item.disk.path,
                    total_sectors=table.total_sectors,
                    unit=table.unit,
                )
            except disk.PlanError as exc:
                ui.message(
                    "Cannot plan this disk",
                    [str(exc)],
                    footer="Press any key to retry",
                )
                continue
            return candidate


def _confirm_lines(plan: InstallLayout, config: InstallConfig) -> list[str]:
    lines = [
        "Disks:   {}".format(", ".join(config.disk_paths)),
        "Root on: {}".format(config.root_disk_path),
    ]
    for item in plan.disks:
        for part in item.partitions:
            label = part.mountpoint or "swap"
            lines.append(
                "  {} {:>4}  {}".format(
                    item.disk_path,
                    str(part.number),
                    "{}  {}  {}".format(
                        disk.human_size(part.size * item.unit),
                        part.fstype,
                        label,
                    ),
                )
            )
    lines.extend(
        [
            "Install: {}".format(", ".join(config.packages)),
            "",
            "This ERASES the selected partitions on every listed disk.",
            "Other partitions are preserved. There is no undo after formatting.",
        ]
    )
    for warning in config.warnings:
        lines.append("Warning: " + warning)
    return lines


def _interactive(
    stdscr,
    args: argparse.Namespace,
    logger: Logger,
    runner: CommandRunner,
    probe: Probe,
) -> int:
    ui = CursesUI(stdscr)
    config = _initial_config(args)
    checks, ok = run_preflight(probe, config, logger)
    lines = [
        "This will install Browneye Linux 13.1 on one or more local GPT disks.",
        "",
    ]
    for check in checks:
        lines.append(
            "[{}] {}: {}".format("x" if check.ok else "!", check.label, check.detail)
        )
    lines.extend(
        [
            "",
            "UEFI only. You can create partitions, assign mount points and use",
            "several disks (for example /home on a second disk). Existing",
            "partitions are preserved unless you mark them for deletion.",
            "There is no undo after formatting begins.",
        ]
    )
    if getattr(probe, "simulated", False):
        lines.extend(
            [
                "",
                "SIMULATION MODE: synthetic disks; no real device is touched.",
                "Mutating commands are written to {}.".format(
                    os.path.join(LOG_DIR, "plan.sh")
                ),
            ]
        )
    if not ok:
        ui.message("Preflight failed", lines, footer="Press any key to exit")
        return 2
    key = ui.message(
        "Browneye Linux 13.1 - Installer"
        + (" (simulation)" if getattr(probe, "simulated", False) else ""),
        lines,
        footer="Enter continue   q quit",
    )
    if key in (ord("q"), 27):
        return 0

    while True:
        probed = probe.probe_disks(refresh=True)
        if not any(item.selectable for item in probed):
            ui.message(
                "No selectable disk",
                [
                    "No disk can be installed to.",
                    "The live media, mounted disks, MBR disks and disks with",
                    "holders or whole-disk filesystems are excluded.",
                ],
                footer="Press any key to exit",
            )
            return 2
        selected = _select_disks(ui, probed)
        if selected is None:
            return 0
        if selected == []:
            continue

        disk_specs: list[DiskSpec] = []
        aborted = False
        for index, item in enumerate(selected):
            initial = _default_disk_spec(item, root_disk=index == 0)
            edited = _edit_disk(
                ui, probe, item, initial, root_disk=index == 0
            )
            if edited is None:
                aborted = True
                break
            disk_specs.append(edited)
        if aborted:
            continue

        root_disk = next(
            (
                spec.path
                for spec in disk_specs
                if any(part.role == "root" for part in spec.partitions)
            ),
            disk_specs[0].path,
        )
        config = InstallConfig(
            layout=InstallSpec(disks=tuple(disk_specs)),
            confirm_disk=root_disk,
            confirm_phrase="ERASE",
            repo=args.repo,
            target=args.target,
            dry_run=args.dry_run,
        )
        # Validate only the layout here.  The admin account and password are
        # entered on the next screen, so a full config.validate() would always
        # fail with "admin password must not be empty" and bounce the user
        # back to disk selection before they ever see the form.
        issues = config.layout.validate()
        if issues:
            ui.message(
                "Invalid layout", issues, footer="Press any key to retry"
            )
            continue
        try:
            plan, probed_used, _regions = build_layout(probe, config)
        except (ConfigError, disk.PlanError) as exc:
            ui.message(
                "Cannot plan the layout",
                [str(exc)],
                footer="Press any key to retry",
            )
            continue

        # Package set ------------------------------------------------
        while True:
            package_rows = [
                Row("Desktop (browneye-base + xfce-desktop)"),
                Row("Base only (no desktop)"),
            ]
            package_choice = ui.menu(
                "Package set",
                "The target always includes the kernel, modules, systemd-boot, "
                "dracut, efibootmgr, dosfstools and dnf.",
                package_rows,
                footer="Up/Down select   Enter continue   Esc back",
                allow_back=True,
            )
            if package_choice in (BACK, QUIT):
                aborted = True
                break
            config.package_set = "desktop" if package_choice == 0 else "base"
            values = ui.form(
                "System options",
                [
                    Field("Hostname", "browneye"),
                    Field("Admin user", "admin"),
                    Field("Password", "", secret=True),
                    Field("Confirm password", "", secret=True),
                ],
                footer="Tab next   Enter continue   Esc back",
                extra_lines=[
                    "The admin user is added to the wheel group.",
                    "Root stays locked; use sudo from the admin account.",
                ],
            )
            if values is None:
                aborted = True
                break
            hostname, admin, password, confirm_password = values
            if password != confirm_password:
                ui.message(
                    "Passwords do not match",
                    ["Re-enter the admin password."],
                    footer="Press any key to retry",
                )
                continue
            config.hostname = hostname
            config.admin_user = admin
            config.admin_password = password
            issues = config.validate()
            if issues:
                ui.message(
                    "Invalid options", issues, footer="Press any key to retry"
                )
                continue
            break
        if aborted:
            continue
        write_probe_snapshot(probe, probed_used, logger)
        break

    # Confirm -------------------------------------------------------
    confirm_lines = _confirm_lines(plan, config)
    typed = ui.confirm_typed(
        "Confirm installation",
        confirm_lines,
        ["Type the root disk path", "Type ERASE"],
        footer="Tab next   Enter confirm   Esc back",
    )
    if typed is None:
        return _interactive(stdscr, args, logger, runner, probe)
    if typed[0].strip() != config.root_disk_path or typed[1].strip() != "ERASE":
        ui.message(
            "Confirmation did not match",
            ["The disk path or ERASE phrase was incorrect.", "Nothing was changed."],
            footer="Press any key to exit",
        )
        return 2
    config.confirm_disk = typed[0].strip()
    config.confirm_phrase = typed[1].strip()

    progress = ui.progress("Installing Browneye Linux", 9)
    logger.console = progress.line
    try:
        execute_install(
            config,
            plan,
            probe,
            runner,
            logger,
            on_step=progress.set_step,
            on_line=progress.line,
        )
    except InstallError as exc:
        logger.console = None
        ui.message(
            "Installation failed",
            [
                "Step: {}".format(exc.step),
                "Error: {}".format(exc.message),
                "",
                "Remedy: {}".format(exc.remedy or "inspect the install log"),
                "Log: {}".format(logger.human_path or LOG_JSONL),
                "",
                "The target may be partially installed. There is no automatic",
                "rollback after formatting begins.",
            ],
            footer="Press any key to exit",
        )
        return 1
    except Exception as exc:
        logger.console = None
        ui.message(
            "Installation failed",
            ["Unexpected error: {}".format(exc), "Log: " + (logger.human_path or LOG_JSONL)],
            footer="Press any key to exit",
        )
        return 1
    logger.console = None
    progress.finish()

    text = [
        "Browneye Linux 13.1 {} on {}.".format(
            "simulation finished" if getattr(probe, "simulated", False)
            else "was installed",
            ", ".join(config.disk_paths),
        ),
        "",
        "Log: {}".format(logger.human_path or LOG_JSONL),
    ]
    if config.dry_run:
        text.extend(
            [
                "",
                "{}: no disk was modified.".format(
                    "SIMULATION" if getattr(probe, "simulated", False) else "DRY RUN"
                ),
                "The exact mutating commands are in {}.".format(
                    os.path.join(LOG_DIR, "plan.sh")
                ),
            ]
        )
        ui.message("Dry run complete", text, footer="Press any key to exit")
        return 0
    text.extend(
        [
            "",
            "Remove the installation media, then press Enter to reboot.",
        ]
    )
    key = ui.message("Installation complete", text, footer="Enter reboot   q exit")
    if args.no_reboot or key in (ord("q"), 27):
        return 0
    try:
        runner.run(("reboot",), step="finish", description="reboot after install")
    except (CommandError, OSError):
        pass
    return 0


def run_curses(
    args: argparse.Namespace,
    logger: Logger,
    runner: CommandRunner,
    probe: Probe,
) -> int:
    try:
        return curses.wrapper(_interactive, args, logger, runner, probe)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        logger.error("curses-failed", error=str(exc))
        print("browneye-installer: {}: {}".format(type(exc).__name__, exc), file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _use_simulated_paths() -> str:
    """Point logs/plans at a writable directory for --simulate."""

    global LOG_DIR, LOG_JSONL, PLAN_JSON
    directory = os.environ.get(
        "BROWNEYE_SIM_DIR", "/tmp/browneye-installer-sim"
    )
    os.makedirs(directory, exist_ok=True)
    LOG_DIR = directory
    LOG_JSONL = os.path.join(directory, "install.jsonl")
    PLAN_JSON = os.path.join(directory, "plan.json")
    return directory


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.simulate:
        sim_dir = _use_simulated_paths()
        print(
            "browneye-installer: simulation mode, logs in {}".format(sim_dir),
            file=sys.stderr,
        )
    logger = Logger(
        LOG_JSONL,
        console=console_line if (args.non_interactive or args.plain) else None,
    )
    logger.session_header(
        version=VERSION,
        dry_run=args.dry_run,
        non_interactive=args.non_interactive,
        plain=args.plain,
        simulate=args.simulate,
    )
    runner = CommandRunner(
        logger,
        dry_run=args.dry_run,
        plan_path=os.path.join(LOG_DIR, "plan.sh"),
    )
    if args.simulate:
        scenario = args.simulate_scenario or "blank"
        probe = simulate_module.SimulatedProbe(runner, scenario)
        logger.info("simulate-mode", scenario=scenario)
    else:
        probe = Probe(runner)
    try:
        if args.non_interactive:
            return run_noninteractive(args, logger, runner, probe)
        if args.plan_json:
            return run_noninteractive(args, logger, runner, probe)
        if args.plain or not (sys.stdin.isatty() and sys.stdout.isatty()):
            return run_plain(args, logger, runner, probe)
        return run_curses(args, logger, runner, probe)
    finally:
        logger.close()


if __name__ == "__main__":
    sys.exit(main())
