"""Installation pipeline and answer-file configuration.

The pipeline is intentionally linear and logs every command.  The disk
planner decides *what* to do; this module decides *when* and performs the
target installation: basefs first, then the target package set, fstab by
UUID, users, initramfs, systemd-boot on the ESP, and the log copy.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

import disk
import layout as layout_module
from layout import InstallLayout, InstallSpec
from log import Logger
from probe import Probe
from runner import Command, CommandError, CommandRunner

MIB = 1024 * 1024
GIB = 1024 * MIB

# sd-boot and the kernel/initramfs live on the ESP.  A 7.3.1 kernel plus its
# generated initramfs is about 48 MiB, so refuse installs that cannot hold a
# couple of generations.
ESP_MIN_FREE_MIB = 256

RELEASEVER = "13.1"
DEFAULT_REPO = "https://repo.pjfox.xyz/packages/13.1/"
FALLBACK_KVER = "7.3.1"

BROWNEYE_BASE_PACKAGES = ("browneye-basefs",)

TARGET_PACKAGES_DESKTOP = (
    "browneye-base-runtime",
    "xfce-desktop",
    "linux-kernel",
    "linux-modules",
    "dracut",
    "efibootmgr",
    "dosfstools",
    "btrfs-progs",
    "sudo",
    "dnf",
)

TARGET_PACKAGES_BASE = tuple(
    pkg for pkg in TARGET_PACKAGES_DESKTOP if pkg != "xfce-desktop"
)

PACKAGE_SETS = {
    "desktop": TARGET_PACKAGES_DESKTOP,
    "base": TARGET_PACKAGES_BASE,
}

_ADMIN_RE = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")
_HOSTNAME_RE = re.compile(
    r"^(?=.{1,63}$)[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$"
)

_ADMIN_KEYS = {"username", "password"}
_CONFIRM_KEYS = {"disk", "phrase"}
_TOP_KEYS = {
    "version",
    "dry_run",
    "layout",
    "package_set",
    "hostname",
    "admin",
    "confirm",
}


class ConfigError(ValueError):
    pass


class InstallError(RuntimeError):
    def __init__(
        self,
        step: str,
        message: str,
        *,
        reversible: bool = False,
        remedy: str = "",
    ) -> None:
        self.step = step
        self.message = message
        self.reversible = reversible
        self.remedy = remedy
        super().__init__(message)


@dataclass
class InstallConfig:
    layout: InstallSpec
    package_set: str = "desktop"
    hostname: str = "browneye"
    admin_user: str = "admin"
    admin_password: str = ""
    confirm_disk: str = ""
    confirm_phrase: str = ""
    repo: str = DEFAULT_REPO
    target: str = "/mnt/browneye"
    dry_run: bool = False
    warnings: list[str] = field(default_factory=list)

    @property
    def packages(self) -> tuple[str, ...]:
        return PACKAGE_SETS.get(self.package_set, TARGET_PACKAGES_DESKTOP)

    @property
    def root_disk_path(self) -> str:
        for item in self.layout.disks:
            if any(part.role == "root" for part in item.partitions):
                return item.path
        return self.layout.disks[0].path if self.layout.disks else ""

    @property
    def disk_paths(self) -> tuple[str, ...]:
        return tuple(item.path for item in self.layout.disks)

    def validate(self) -> list[str]:
        issues: list[str] = []
        issues.extend(self.layout.validate())
        root_disk = self.root_disk_path
        if not root_disk or not root_disk.startswith("/dev/"):
            issues.append("the layout has no root disk")
        elif self.confirm_disk != root_disk:
            issues.append(
                "confirmation disk path does not match the root disk {}".format(
                    root_disk
                )
            )
        if self.confirm_phrase != "ERASE":
            issues.append("confirmation phrase must be exactly ERASE")
        if not _ADMIN_RE.match(self.admin_user or ""):
            issues.append(
                "admin user must start with a lower-case letter or underscore "
                "and contain only lower-case letters, digits, '_' or '-'"
            )
        if self.admin_user == "root":
            issues.append("the admin user must not be root")
        if not self.admin_password:
            issues.append("admin password must not be empty")
        elif ":" in self.admin_password or "\n" in self.admin_password:
            issues.append("admin password must not contain ':' or a newline")
        if not _HOSTNAME_RE.match(self.hostname or ""):
            issues.append("hostname is not a valid DNS label")
        if self.package_set not in PACKAGE_SETS:
            issues.append("package_set must be 'desktop' or 'base'")
        if "://" not in self.repo and not os.path.isabs(self.repo):
            issues.append("repo must be an http(s)/ftp URL or an absolute path")
        if not os.path.isabs(self.target):
            issues.append("target path must be absolute")
        return issues

    def public_dict(self) -> dict[str, Any]:
        return {
            "layout": self.layout.to_dict(),
            "root_disk": self.root_disk_path,
            "package_set": self.package_set,
            "hostname": self.hostname,
            "admin": {"username": self.admin_user, "password": "<redacted>"},
            "repo": self.repo,
            "target": self.target,
            "dry_run": self.dry_run,
            "warnings": list(self.warnings),
        }

    @classmethod
    def from_mapping(
        cls,
        data: dict[str, Any],
        *,
        repo: str = DEFAULT_REPO,
        target: str = "/mnt/browneye",
        dry_run: bool = False,
    ) -> "InstallConfig":
        if not isinstance(data, dict):
            raise ConfigError("answer file must contain a JSON object")
        unknown = set(data) - _TOP_KEYS
        if unknown:
            raise ConfigError(
                "unknown answer-file keys: " + ", ".join(sorted(unknown))
            )
        version = data.get("version", 2)
        if version != 2:
            raise ConfigError(
                "unsupported answer-file version: {!r}; version 2 is required".format(
                    version
                )
            )
        try:
            spec = InstallSpec.from_mapping(data.get("layout"))
        except ValueError as exc:
            raise ConfigError(str(exc)) from exc
        admin = data.get("admin")
        if not isinstance(admin, dict):
            raise ConfigError("answer file has no admin object")
        unknown_admin = set(admin) - _ADMIN_KEYS
        if unknown_admin:
            raise ConfigError(
                "unknown admin keys: " + ", ".join(sorted(unknown_admin))
            )
        confirm = data.get("confirm")
        if not isinstance(confirm, dict):
            raise ConfigError("answer file has no confirm object")
        unknown_confirm = set(confirm) - _CONFIRM_KEYS
        if unknown_confirm:
            raise ConfigError(
                "unknown confirm keys: " + ", ".join(sorted(unknown_confirm))
            )
        config = cls(
            layout=spec,
            package_set=str(data.get("package_set", "desktop")),
            hostname=str(data.get("hostname", "browneye")),
            admin_user=str(admin.get("username", "admin")),
            admin_password=str(admin.get("password", "")),
            confirm_disk=str(confirm.get("disk", "")),
            confirm_phrase=str(confirm.get("phrase", "")),
            repo=repo,
            target=target,
            dry_run=dry_run or bool(data.get("dry_run", False)),
        )
        return config


@dataclass(frozen=True)
class Step:
    name: str
    title: str


class Installer:
    def __init__(
        self,
        config: InstallConfig,
        runner: CommandRunner,
        logger: Logger,
        probe: Probe,
        layout: InstallLayout,
        *,
        on_step: Callable[[int, int, str], None] | None = None,
        on_line: Callable[[str], None] | None = None,
    ) -> None:
        self.config = config
        self.runner = runner
        self.logger = logger
        self.probe = probe
        self.layout = layout
        self.on_step = on_step
        self.on_line = on_line
        self.kver = FALLBACK_KVER
        self.current_step = ""
        self.root_mounted = False
        self.esp_mounted = False
        self.bind_mounted = False
        self.swap_on: list[disk.PlannedPartition] = []
        self.destructive_started = False
        self.backup_dir = "/run/browneye/backup"
        self.dnf_cache = "/run/browneye/dnf-cache"
        self.dnf_persist = "/run/browneye/dnf-persist"
        self.log_dir = os.path.dirname(logger.path) if logger.path else "/run/browneye"
        self.target = config.target

    # ------------------------------------------------------------------
    # Step orchestration
    # ------------------------------------------------------------------
    def steps(self) -> tuple[Step, ...]:
        return (
            Step("partition", "Partitioning the disk"),
            Step("format", "Creating filesystems"),
            Step("mount", "Mounting the target"),
            Step("basefs", "Installing the base filesystem"),
            Step("packages", "Installing packages"),
            Step("configure", "Configuring the system"),
            Step("initramfs", "Generating the initramfs"),
            Step("bootloader", "Installing the bootloader"),
            Step("finish", "Copying logs and unmounting"),
        )

    def run(self) -> None:
        steps = self.steps()
        total = len(steps)
        self.logger.info(
            "install-begin",
            disks=list(self.config.disk_paths),
            layout=self.layout.to_dict(),
            packages=list(self.config.packages),
        )
        try:
            for index, step in enumerate(steps, 1):
                self.current_step = step.name
                self.logger.step_start(step.name, index, total)
                if self.on_step is not None:
                    self.on_step(index, total, step.title)
                try:
                    getattr(self, "step_" + step.name)()
                except InstallError:
                    raise
                except CommandError as exc:
                    raise InstallError(
                        step.name,
                        str(exc),
                        reversible=not self.destructive_started,
                        remedy=self._remedy_for(step.name),
                    ) from exc
                except Exception as exc:  # never leave a bare traceback in the UI
                    raise InstallError(
                        step.name,
                        f"{type(exc).__name__}: {exc}",
                        reversible=not self.destructive_started,
                        remedy=self._remedy_for(step.name),
                    ) from exc
                self.logger.step_done(step.name, index, total)
            self.logger.info("install-complete", disks=list(self.config.disk_paths))
        except InstallError as exc:
            self.logger.error(
                "install-failed",
                step=exc.step,
                message=exc.message,
                reversible=exc.reversible,
                remedy=exc.remedy,
            )
            self._copy_failure_log()
            self._cleanup_mounts()
            raise

    @staticmethod
    def _remedy_for(step: str) -> str:
        if step == "partition":
            return "the original table is restored from the snapshot when possible"
        if step == "format":
            return "formatting already started; re-run the install with an explicit confirmation"
        return "the target was left as-is; inspect the log and retry the step"

    def _line(self, text: str) -> None:
        if self.on_line is not None and text:
            self.on_line(text)

    def _run(self, command: Command, *, streaming: bool = False) -> Any:
        if streaming:
            return self.runner.run_streaming(
                command.argv,
                self._line,
                step=command.step,
                description=command.description,
                stdin=command.stdin,
                stdin_redacted=command.stdin_redacted,
                allow_failure=command.allow_failure,
                timeout=command.timeout,
                cwd=command.cwd,
            )
        return self.runner.run_command(command, on_line=self._line)

    # ------------------------------------------------------------------
    # Steps
    # ------------------------------------------------------------------
    def step_partition(self) -> None:
        self.logger.plan(self.layout.to_dict())
        written: list[layout_module.DiskLayout] = []

        def rollback_all(current: layout_module.DiskLayout, reason: str) -> None:
            self._rollback(current, reason)
            for previous in reversed(written):
                if previous is not current:
                    self._rollback(previous, reason)

        for item in self.layout.disks:
            if not item.changed:
                continue
            # 1. Snapshot.  A failure here is safe: nothing has changed yet.
            for command in layout_module.snapshot_commands(item, self.backup_dir):
                self._run(command)
            # 2. Delete selected entries and write the full replacement table.
            try:
                for command in layout_module.delete_commands(item):
                    self._run(command)
                for command in layout_module.write_table_commands(item):
                    self._run(command)
            except CommandError as exc:
                self.logger.error(
                    "partition-write-failed", disk=item.disk_path, error=str(exc)
                )
                rollback_all(item, "partition table write failed")
                raise InstallError(
                    "partition",
                    "writing the replacement partition table on {} failed: {}".format(
                        item.disk_path, exc
                    ),
                    reversible=True,
                    remedy="the saved tables were restored",
                ) from exc

            written.append(item)
            self.destructive_started = True

            if self.runner.dry_run:
                continue
            probed = self.probe.find_disk(item.disk_path, refresh=True)
            if probed is None:
                rollback_all(item, "selected disk disappeared")
                raise InstallError(
                    "partition",
                    "the selected disk {} is no longer present".format(
                        item.disk_path
                    ),
                    reversible=True,
                )
            after = self.probe.read_table(probed.disk)
            issues = layout_module.verify_preserved(item, after)
            issues.extend(layout_module.verify_planned(item, after))
            if issues:
                self.logger.error(
                    "partition-verify-failed", disk=item.disk_path, issues=issues
                )
                rollback_all(item, "partition preservation check failed")
                raise InstallError(
                    "partition",
                    "the new partition table on {} did not preserve existing "
                    "entries: {}".format(item.disk_path, "; ".join(issues)),
                    reversible=True,
                    remedy="the saved tables were restored; no filesystem was written",
                )
            self.logger.info(
                "partition-verified", disk=item.disk_path, table=after
            )
        if self.runner.dry_run:
            self.logger.info("partition-plan-recorded")

    def _rollback(self, item: layout_module.DiskLayout, reason: str) -> None:
        if self.runner.dry_run:
            return
        self.logger.warning(
            "rollback-start", disk=item.disk_path, reason=reason
        )
        try:
            for command in layout_module.rollback_commands(
                item, self.backup_dir
            ):
                self._run(command)
            self.logger.info("rollback-done", disk=item.disk_path)
        except CommandError as exc:
            self.logger.error("rollback-failed", error=str(exc))

    def step_format(self) -> None:
        if not self.runner.dry_run and not self.probe.wait_for_partuuids(
            self.layout
        ):
            raise InstallError(
                "format",
                "the new partition device nodes did not appear (udev did not settle)",
                reversible=True,
            )
        self.destructive_started = True
        for command in layout_module.all_format_commands(self.layout):
            self._run(command)
        if self.runner.dry_run:
            self.logger.info("format-plan-recorded")
            return
        for check in layout_module.all_format_checks(self.layout):
            type_result = self._run(check.type_command)
            uuid_result = self._run(check.uuid_command)
            actual_type = (type_result.output or "").strip().lower()
            actual_uuid = (uuid_result.output or "").strip()
            if actual_type != check.expected_fstype:
                raise InstallError(
                    "format",
                    "partition {} is {!r}, expected {}".format(
                        check.part.number,
                        actual_type,
                        check.expected_fstype,
                    ),
                    reversible=False,
                )
            expected_uuid = check.part.fs_uuid
            if expected_uuid:
                if check.expected_fstype == "vfat":
                    matches = actual_uuid.upper() == expected_uuid.upper()
                else:
                    matches = actual_uuid.lower() == expected_uuid.lower()
                if not matches:
                    raise InstallError(
                        "format",
                        "partition {} UUID mismatch: {} != {}".format(
                            check.part.number, actual_uuid, expected_uuid
                        ),
                        reversible=False,
                    )
        # A read-only filesystem check is informative, not a hard failure right
        # after mkfs.  Do it so a broken image is visible in the log.
        for part in self.layout.partitions:
            if part.existing and not part.format:
                continue
            device = self.probe.resolve_partition(part)
            fstype = (part.fstype or "").lower()
            if fstype == "vfat":
                self.runner.run(
                    ("fsck.fat", "-n", device),
                    step="format",
                    read_only=True,
                    destructive=False,
                    allow_failure=True,
                    description="check the FAT filesystem on partition {}".format(
                        part.number
                    ),
                )
            elif fstype == "ext4":
                self.runner.run(
                    ("e2fsck", "-fn", device),
                    step="format",
                    read_only=True,
                    destructive=False,
                    allow_failure=True,
                    description="check the ext4 filesystem on partition {}".format(
                        part.number
                    ),
                )

    def step_mount(self) -> None:
        root = self.layout.root
        esp = self.layout.esp
        if root is None or esp is None:
            raise InstallError(
                "mount",
                "the layout has no root partition or no ESP",
                reversible=True,
            )
        root_dev = self.probe.resolve_partition(root)
        esp_dev = self.probe.resolve_partition(esp)
        self.runner.makedirs(self.target, step="mount")
        self.runner.run(
            ("mount", "-o", "rw,noatime", root_dev, self.target),
            step="mount",
            description="mount the new root filesystem",
        )
        self.root_mounted = True
        boot = os.path.join(self.target, "boot")
        self.runner.makedirs(boot, step="mount")
        self.runner.run(
            (
                "mount",
                "-o",
                "rw,umask=0077",
                esp_dev,
                boot,
            ),
            step="mount",
            description="mount the EFI System Partition at /boot",
        )
        self.esp_mounted = True
        if not self.runner.dry_run:
            stats = os.statvfs(boot)
            free_mib = (stats.f_bavail * stats.f_frsize) // MIB
            if free_mib < ESP_MIN_FREE_MIB:
                raise InstallError(
                    "mount",
                    "the ESP has only {} MiB free, but systemd-boot keeps "
                    "the kernel and initramfs on it".format(free_mib),
                    reversible=True,
                    remedy="delete the partition and let the installer "
                           "create a larger ESP (1 GiB is recommended)",
                )
        # Data partitions are mounted before the bind mounts so package
        # scriptlets and useradd see the final directory tree.
        for part in sorted(self.layout.data, key=layout_module.mount_sort_key):
            mountpoint = part.mountpoint or ""
            destination = self.target + mountpoint
            if mountpoint != "/":
                self.runner.makedirs(destination, step="mount")
            options = "rw,umask=0077" if part.fstype == "vfat" else "rw,noatime"
            self.runner.run(
                ("mount", "-o", options, self.probe.resolve_partition(part), destination),
                step="mount",
                description="mount {} at {}".format(mountpoint, mountpoint),
            )
        for part in self.layout.swaps:
            self.runner.run(
                ("swapon", self.probe.resolve_partition(part)),
                step="mount",
                description="enable swap on partition {}".format(part.number),
            )
            self.swap_on.append(part)
        for name in ("dev", "proc", "sys", "run"):
            self.runner.makedirs(os.path.join(self.target, name), step="mount")
        for name in ("dev", "proc", "sys", "run"):
            self.runner.run(
                ("mount", "--bind", "/" + name, os.path.join(self.target, name)),
                step="mount",
                description=f"bind-mount /{name} for package scriptlets",
            )
        self.bind_mounted = True
        efivars = "/sys/firmware/efi/efivars"
        if os.path.isdir(efivars):
            target_efivars = os.path.join(self.target, "sys", "firmware", "efi", "efivars")
            self.runner.makedirs(target_efivars, step="mount")
            self.runner.run(
                ("mount", "-t", "efivarfs", "efivarfs", target_efivars),
                step="mount",
                description="mount efivarfs for bootctl and efibootmgr",
                allow_failure=True,
            )

    def _dnf_install(
        self,
        packages: Sequence[str],
        *,
        step: str,
        weak_deps: bool,
        description: str,
    ) -> Any:
        self.runner.makedirs(self.dnf_cache, step=step, allow_failure=True)
        self.runner.makedirs(self.dnf_persist, step=step, allow_failure=True)
        repo = self.config.repo
        repo_source = repo if "://" in repo else "file://" + repo
        argv = [
            "dnf",
            "-y",
            "--nogpgcheck",
            "--installroot",
            self.target,
            "--releasever=" + RELEASEVER,
            "--disablerepo=*",
            "--repofrompath=browneye," + repo_source,
            "--setopt=install_weak_deps=" + ("True" if weak_deps else "False"),
            "--setopt=cachedir=" + self.dnf_cache,
            "--setopt=persistdir=" + self.dnf_persist,
            "install",
            *packages,
        ]
        result = self.runner.run_streaming(
            argv,
            self._line,
            step=step,
            description=description,
        )
        if not self.runner.dry_run:
            fatal = self._dnf_fatal_lines(result.output)
            if fatal:
                raise InstallError(
                    step,
                    "dnf reported {}; see the install log".format(fatal[0]),
                    reversible=False,
                    remedy="retry the package transaction after inspecting the log",
                )
        return result

    @staticmethod
    def _dnf_fatal_lines(output: str) -> list[str]:
        fatal: list[str] = []
        for line in output.splitlines():
            stripped = line.strip()
            lowered = stripped.lower()
            if lowered.startswith("error:") or "scriptlet failed" in lowered:
                fatal.append(stripped[:300])
        return fatal

    def step_basefs(self) -> None:
        self._dnf_install(
            BROWNEYE_BASE_PACKAGES,
            step="basefs",
            weak_deps=False,
            description="install browneye-basefs first so /bin/sh exists for scriptlets",
        )
        self.logger.info("basefs-installed")

    def step_packages(self) -> None:
        self._dnf_install(
            self.config.packages,
            step="packages",
            weak_deps=True,
            description="install the target package set with scriptlets enabled",
        )
        self.destructive_started = True
        if self.runner.dry_run:
            self.kver = FALLBACK_KVER
            return
        result = self.runner.run(
            (
                "rpm",
                "--root",
                self.target,
                "-q",
                *BROWNEYE_BASE_PACKAGES,
                *self.config.packages,
            ),
            step="packages",
            read_only=True,
            destructive=False,
            allow_failure=True,
            description="verify the installed package set",
        )
        missing = [
            line
            for line in result.output.splitlines()
            if "is not installed" in line or line.strip().startswith("package ")
        ]
        if missing:
            raise InstallError(
                "packages",
                "package verification failed: " + "; ".join(missing[:8]),
                reversible=False,
            )
        if not result.ok:
            raise InstallError(
                "packages",
                "rpm verification failed: " + result.output[-500:],
                reversible=False,
            )
        self.kver = self._detect_kver()
        self.logger.info("kernel-version", kver=self.kver)

    def _detect_kver(self) -> str:
        modules = os.path.join(self.target, "usr", "lib", "modules")
        try:
            entries = [
                name
                for name in os.listdir(modules)
                if os.path.isdir(os.path.join(modules, name))
            ]
        except OSError:
            entries = []
        if not entries:
            raise InstallError(
                "packages",
                "no kernel modules directory found in the target",
                reversible=False,
            )

        def key(value: str) -> tuple[int, ...]:
            return tuple(int(part) for part in re.split(r"[^0-9]+", value) if part)

        return max(entries, key=key)

    def step_configure(self) -> None:
        self._write_fstab()
        self._write_network_files()
        self._write_repo_file()
        self._configure_systemd()
        self._configure_users()

    def _write_repo_file(self) -> None:
        """Configure the repository the installer used, for later use.

        Installs are network-only, so the target needs the source in
        /etc/yum.repos.d to `dnf install` anything afterwards.
        """
        source = self.config.repo
        if "://" not in source:
            source = "file://" + source
        repos_dir = os.path.join(self.target, "etc", "yum.repos.d")
        self.runner.run(
            ("install", "-dm0755", repos_dir),
            step="configure",
            description="create the repository directory")
        self.runner.write_file(
            os.path.join(repos_dir, "browneye-13.1.repo"),
            "[browneye-13.1]\n"
            "name=Browneye Linux 13.1\n"
            "baseurl=" + source + "\n"
            "enabled=1\n"
            "gpgcheck=0\n"
            "repo_gpgcheck=0\n"
            "skip_if_unavailable=1\n",
            step="configure",
        )

    def _uuid_ref(self, part: disk.PlannedPartition) -> str:
        if part.fs_uuid:
            return "UUID=" + part.fs_uuid
        return "PARTUUID=" + part.partuuid

    def _fstab_entry(self, part: disk.PlannedPartition) -> str:
        if part.role == "swap":
            return "{} none swap sw 0 0".format(self._uuid_ref(part))
        mountpoint = part.mountpoint or ""
        fstype = part.fstype or "auto"
        if part.role == "root":
            options = "defaults,noatime"
            passno = 1
        elif fstype == "vfat":
            options = "umask=0077,shortname=winnt"
            passno = 2
        else:
            options = "defaults,noatime"
            passno = 2
        return "{} {} {} {} 0 {}".format(
            self._uuid_ref(part), mountpoint, fstype, options, passno
        )

    def _write_fstab(self) -> None:
        lines = [
            "# <file system> <mount point> <type> <options> <dump> <pass>",
        ]
        root = self.layout.root
        esp = self.layout.esp
        if root is not None:
            lines.append(self._fstab_entry(root))
        if esp is not None:
            lines.append(self._fstab_entry(esp))
        for part in sorted(self.layout.data, key=layout_module.mount_sort_key):
            lines.append(self._fstab_entry(part))
        for part in self.layout.swaps:
            lines.append(self._fstab_entry(part))
        lines.append("tmpfs /tmp tmpfs defaults 0 0")
        text = "\n".join(lines) + "\n"
        self.runner.write_file(
            os.path.join(self.target, "etc", "fstab"),
            text,
            mode=0o644,
            step="configure",
            log_content=True,
        )

    def _write_network_files(self) -> None:
        hostname = self.config.hostname
        self.runner.write_file(
            os.path.join(self.target, "etc", "hostname"),
            hostname + "\n",
            mode=0o644,
            step="configure",
        )
        hosts_path = os.path.join(self.target, "etc", "hosts")
        existing = self.runner.read_text(hosts_path)
        if existing is None:
            existing = (
                "127.0.0.1\tlocalhost\n"
                "::1\t\tlocalhost\n"
            )
        if "127.0.1.1" in existing:
            text = existing
        else:
            if existing and not existing.endswith("\n"):
                existing += "\n"
            text = existing + "127.0.1.1\t{}\n".format(hostname)
        self.runner.write_file(hosts_path, text, mode=0o644, step="configure")

    def _configure_systemd(self) -> None:
        self.runner.run(
            ("chroot", self.target, "/usr/bin/systemd-sysusers"),
            step="configure",
            description="materialize system users and groups",
            allow_failure=True,
        )
        self.runner.run(
            ("chroot", self.target, "/usr/sbin/ldconfig"),
            step="configure",
            description="refresh the dynamic linker cache",
            allow_failure=True,
        )
        self.runner.run(
            ("chroot", self.target, "/usr/bin/systemctl", "--root=/", "preset-all"),
            step="configure",
            description="apply the systemd presets",
        )
        target = "graphical.target" if self.config.package_set == "desktop" else "multi-user.target"
        self.runner.run(
            ("chroot", self.target, "/usr/bin/systemctl", "--root=/", "set-default", target),
            step="configure",
            description="set the default systemd target",
        )

    def _configure_users(self) -> None:
        user = self.config.admin_user
        if not self.runner.dry_run:
            group = self.runner.run(
                ("chroot", self.target, "/usr/bin/getent", "group", "wheel"),
                step="configure",
                read_only=True,
                destructive=False,
                allow_failure=True,
                description="check for the wheel group",
            )
            if not group.ok:
                self.runner.run(
                    ("chroot", self.target, "/usr/sbin/groupadd", "-r", "wheel"),
                    step="configure",
                    description="create the wheel group",
                )
            exists = self.runner.run(
                ("chroot", self.target, "/usr/bin/getent", "passwd", user),
                step="configure",
                read_only=True,
                destructive=False,
                allow_failure=True,
                description="check whether the admin user exists",
            )
            if exists.ok:
                self.runner.run(
                    (
                        "chroot",
                        self.target,
                        "/usr/sbin/usermod",
                        "-aG",
                        "wheel",
                        "-s",
                        "/bin/bash",
                        user,
                    ),
                    step="configure",
                    description="ensure the admin user is in wheel",
                )
            else:
                self.runner.run(
                    (
                        "chroot",
                        self.target,
                        "/usr/sbin/useradd",
                        "-m",
                        "-G",
                        "wheel",
                        "-s",
                        "/bin/bash",
                        user,
                    ),
                    step="configure",
                    description="create the admin user",
                )
        else:
            # Dry-run: record the normal path.  The plan does not depend on
            # whether the user already exists in an unmounted target.
            self.runner.run(
                (
                    "chroot",
                    self.target,
                    "/usr/sbin/useradd",
                    "-m",
                    "-G",
                    "wheel",
                    "-s",
                    "/bin/bash",
                    user,
                ),
                step="configure",
                description="create the admin user",
            )

        self.runner.run(
            (
                "chroot",
                self.target,
                "/usr/sbin/usermod",
                "--add-subuids",
                "100000-165535",
                "--add-subgids",
                "100000-165535",
                user,
            ),
            step="configure",
            allow_failure=True,
            description="give the admin user a rootless podman id range",
        )
        self.runner.run(
            ("chroot", self.target, "/usr/sbin/chpasswd"),
            step="configure",
            stdin="{}:{}\n".format(user, self.config.admin_password),
            stdin_redacted=True,
            description="set the admin password from stdin (not argv)",
        )
        self.runner.run(
            ("chroot", self.target, "/usr/bin/passwd", "-l", "root"),
            step="configure",
            description="lock the root account; administration is via sudo",
        )
        marker = os.path.join(
            self.target, "var", "lib", "browneye", "firstboot-root-password.done"
        )
        self.runner.write_file(
            marker,
            "root locked by the installer; administrative access is via {}\n".format(user),
            mode=0o644,
            step="configure",
        )

    def step_initramfs(self) -> None:
        if not self.runner.dry_run:
            # Detect again in case the packages step was resumed.
            if not self.kver:
                self.kver = self._detect_kver()
        self.runner.run(
            ("chroot", self.target, "/usr/sbin/depmod", self.kver),
            step="initramfs",
            description="update module dependencies",
            allow_failure=True,
        )
        self.runner.run(
            (
                "chroot",
                self.target,
                "/usr/bin/dracut",
                "--force",
                "--no-hostonly",
                "--kver",
                self.kver,
                "/boot/initramfs-{}.img".format(self.kver),
            ),
            step="initramfs",
            description="build a generic initramfs",
        )
        if not self.runner.dry_run:
            image = os.path.join(
                self.target, "boot", "initramfs-{}.img".format(self.kver)
            )
            if not os.path.isfile(image) or os.path.getsize(image) == 0:
                raise InstallError(
                    "initramfs",
                    "dracut did not produce a usable initramfs",
                    reversible=False,
                    remedy="retry dracut inside the target chroot",
                )
        self.runner.run(
            ("chroot", self.target, "/usr/sbin/ldconfig"),
            step="initramfs",
            description="refresh the dynamic linker cache",
            allow_failure=True,
        )

    def step_bootloader(self) -> None:
        # bootctl writes EFI/systemd/systemd-bootx64.efi and the removable
        # EFI/BOOT/BOOTX64.EFI fallback.  --no-variables leaves NVRAM to
        # efibootmgr below, the same split grub-install --no-nvram used.
        self.runner.run(
            (
                "chroot",
                self.target,
                "/usr/bin/bootctl",
                "--esp-path=/boot",
                "--no-variables",
                "install",
            ),
            step="bootloader",
            description="install systemd-boot on the ESP without touching NVRAM",
        )
        self.runner.write_file(
            os.path.join(self.target, "boot", "loader", "loader.conf"),
            self._loader_conf(),
            mode=0o644,
            step="bootloader",
        )
        self.runner.write_file(
            os.path.join(self.target, "boot", "loader", "entries", self._entry_name()),
            self._loader_entry(),
            mode=0o644,
            step="bootloader",
        )
        # Future kernel packages read this and write matching loader entries.
        self.runner.write_file(
            os.path.join(self.target, "etc", "kernel", "cmdline"),
            self._kernel_cmdline() + "\n",
            mode=0o644,
            step="bootloader",
        )
        if not self.runner.dry_run:
            expected = (
                os.path.join("boot", "EFI", "systemd", "systemd-bootx64.efi"),
                os.path.join("boot", "EFI", "BOOT", "BOOTX64.EFI"),
                os.path.join("boot", "loader", "entries", self._entry_name()),
            )
            missing = [
                rel for rel in expected
                if not os.path.isfile(os.path.join(self.target, rel))
            ]
            if missing:
                raise InstallError(
                    "bootloader",
                    "the systemd-boot installation is incomplete: "
                    + ", ".join(missing),
                    reversible=False,
                )
        esp = self.layout.esp
        esp_disk = self.layout.disk_for(esp) if esp is not None else None
        if esp is None or esp_disk is None:
            raise InstallError(
                "bootloader",
                "the layout has no ESP disk",
                reversible=False,
            )
        self.runner.run(
            (
                "efibootmgr",
                "--create",
                "--disk",
                esp_disk.disk_path,
                "--part",
                str(esp.number),
                "--label",
                "Browneye Linux",
                "--loader",
                r"\EFI\systemd\systemd-bootx64.efi",
            ),
            step="bootloader",
            description="add a firmware boot entry (fallback if NVRAM is read-only)",
            allow_failure=True,
        )
        self.runner.run(
            ("efibootmgr", "-v"),
            step="bootloader",
            description="record the firmware boot entries",
            read_only=True,
            destructive=False,
            allow_failure=True,
        )

    def _entry_name(self) -> str:
        return "browneye-{}.conf".format(self.kver)

    def _kernel_cmdline(self) -> str:
        root = self.layout.root
        if root is None:
            raise InstallError(
                "bootloader",
                "the layout has no root partition",
                reversible=False,
            )
        return "root={} ro rootwait".format(self._uuid_ref(root))

    def _loader_conf(self) -> str:
        return "\n".join(
            [
                "default browneye-*",
                "timeout 3",
                "console-mode keep",
                "editor no",
                "",
            ]
        )

    def _loader_entry(self) -> str:
        # The kernel image and initramfs are flat files on the ESP: the
        # installer runs kernel-install only through the package scriptlets,
        # and sd-boot resolves these paths relative to the ESP.
        return "\n".join(
            [
                "title Browneye Linux 13.1 ({})".format(self.kver),
                "linux /vmlinuz-{}".format(self.kver),
                "initrd /initramfs-{}.img".format(self.kver),
                "options " + self._kernel_cmdline(),
                "",
            ]
        )

    def step_finish(self) -> None:
        self.logger.flush()
        self._copy_logs_to_target()
        self._copy_logs_to_esp()
        if not self.runner.dry_run:
            self.runner.run(
                ("sync",),
                step="finish",
                description="flush filesystem buffers before unmounting",
            )
        self._cleanup_mounts(required=True)
        self.logger.info("install-finished")

    # ------------------------------------------------------------------
    # Log copying and cleanup
    # ------------------------------------------------------------------
    def _copy_file(self, source: str, destination: str, *, step: str, allow_failure: bool = False) -> None:
        if not os.path.exists(source):
            return
        self.runner.run(
            ("install", "-D", "-m", "0644", source, destination),
            step=step,
            description="copy {} to {}".format(source, destination),
            allow_failure=allow_failure,
        )

    def _copy_logs_to_target(self) -> None:
        directory = os.path.join(self.target, "var", "log", "browneye-install")
        self.runner.makedirs(directory, step="finish")
        for name in ("install.jsonl", "install.log", "plan.json", "plan.sh", "probe.json"):
            source = os.path.join(self.log_dir, name)
            if not os.path.exists(source):
                continue
            self._copy_file(
                source,
                os.path.join(directory, name),
                step="finish",
            )
        if not self.runner.dry_run:
            self.runner.run(
                ("sync",),
                step="finish",
                description="flush the copied logs",
            )

    def _copy_logs_to_esp(self) -> None:
        if not self.esp_mounted and not self.runner.dry_run:
            return
        esp = os.path.join(self.target, "boot")
        self._copy_file(
            os.path.join(self.log_dir, "install.jsonl"),
            os.path.join(esp, "browneye-install.jsonl"),
            step="finish",
            allow_failure=True,
        )
        self._copy_file(
            os.path.join(self.log_dir, "install.log"),
            os.path.join(esp, "browneye-install.log"),
            step="finish",
            allow_failure=True,
        )

    def _copy_failure_log(self) -> None:
        if self.runner.dry_run:
            return
        self.logger.flush()
        if self.esp_mounted:
            esp = os.path.join(self.target, "boot")
            self._copy_file(
                os.path.join(self.log_dir, "install.jsonl"),
                os.path.join(esp, "browneye-install-failure.jsonl"),
                step="failure",
                allow_failure=True,
            )
            self._copy_file(
                os.path.join(self.log_dir, "install.log"),
                os.path.join(esp, "browneye-install-failure.log"),
                step="failure",
                allow_failure=True,
            )
            return
        # The target may not be mounted yet (for example a failure during
        # partitioning/formatting).  Try the ESP directly so the log survives
        # the reboot; this is strictly best effort.
        if not self.destructive_started:
            return
        esp = self.layout.esp
        if esp is None:
            return
        mountpoint = "/run/browneye/esp-failure"
        self.runner.makedirs(mountpoint, step="failure", allow_failure=True)
        mounted = self.runner.run(
            (
                "mount",
                "-o",
                "rw,umask=0077",
                esp.by_partuuid,
                mountpoint,
            ),
            step="failure",
            description="mount the ESP to save the failure log",
            allow_failure=True,
        )
        if not mounted.ok:
            return
        try:
            self._copy_file(
                os.path.join(self.log_dir, "install.jsonl"),
                os.path.join(mountpoint, "browneye-install-failure.jsonl"),
                step="failure",
                allow_failure=True,
            )
            self._copy_file(
                os.path.join(self.log_dir, "install.log"),
                os.path.join(mountpoint, "browneye-install-failure.log"),
                step="failure",
                allow_failure=True,
            )
        finally:
            self.runner.run(
                ("umount", mountpoint),
                step="failure",
                description="unmount the failure-log ESP",
                allow_failure=True,
            )

    def _cleanup_mounts(self, *, required: bool = False) -> None:
        swap_on = list(self.swap_on)
        self.swap_on = []
        for part in swap_on:
            self.runner.run(
                ("swapoff", self.probe.resolve_partition(part)),
                step="finish",
                description="disable swap on partition {}".format(part.number),
                allow_failure=True,
            )
        if not (self.root_mounted or self.esp_mounted or self.bind_mounted):
            return
        if self.runner.dry_run:
            self.runner.run(
                ("umount", "-R", self.target),
                step="finish",
                description="unmount the target and all bind mounts",
                allow_failure=not required,
            )
            self.root_mounted = self.esp_mounted = self.bind_mounted = False
            return
        try:
            self.runner.run(
                ("umount", "-R", self.target),
                step="finish",
                description="unmount the target and all bind mounts",
                allow_failure=not required,
            )
            self.root_mounted = self.esp_mounted = self.bind_mounted = False
        except CommandError:
            self.logger.error("unmount-failed", target=self.target)
            if required:
                raise InstallError(
                    "finish",
                    "the target could not be unmounted; it may be busy",
                    reversible=False,
                    remedy="unmount {} manually before rebooting".format(self.target),
                )
