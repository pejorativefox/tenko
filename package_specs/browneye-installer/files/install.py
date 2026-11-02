"""Installation pipeline and answer-file configuration.

The pipeline is intentionally linear and logs every command.  The disk
planner decides *what* to do; this module decides *when* and performs the
target installation: basefs first, then the target package set, fstab by
UUID, users, initramfs, GRUB UEFI, the removable fallback, and the log copy.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Sequence

import disk
from disk import LayoutPlan
from log import Logger
from probe import Probe
from runner import Command, CommandError, CommandRunner

MIB = 1024 * 1024
GIB = 1024 * MIB

RELEASEVER = "13.1"
FALLBACK_KVER = "7.2.6"

BROWNEYE_BASE_PACKAGES = ("browneye-basefs",)

TARGET_PACKAGES_DESKTOP = (
    "browneye-base",
    "xfce-desktop",
    "linux-kernel",
    "linux-modules",
    "dracut",
    "grub",
    "efibootmgr",
    "dosfstools",
    "sudo",
    "dnf",
    "opencode-bin",
    "herdr",
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

_DISK_KEYS = {"path", "serial", "size_bytes", "model"}
_ADMIN_KEYS = {"username", "password"}
_CONFIRM_KEYS = {"disk", "phrase"}
_TOP_KEYS = {
    "version",
    "dry_run",
    "disk",
    "delete_partitions",
    "region",
    "esp_mib",
    "root_mib",
    "swap_mib",
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
    disk_path: str
    disk_serial: str | None = None
    disk_size_bytes: int | None = None
    disk_model: str | None = None
    delete_partitions: tuple[int, ...] = ()
    region_start_mib: int | None = None
    esp_mib: int = 512
    root_mib: int | None = None
    swap_mib: int | None = 2048
    package_set: str = "desktop"
    hostname: str = "browneye"
    admin_user: str = "admin"
    admin_password: str = ""
    confirm_disk: str = ""
    confirm_phrase: str = ""
    repo: str = "/run/initramfs/live/repo"
    target: str = "/mnt/browneye"
    dry_run: bool = False

    @property
    def packages(self) -> tuple[str, ...]:
        return PACKAGE_SETS.get(self.package_set, TARGET_PACKAGES_DESKTOP)

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.disk_path or not self.disk_path.startswith("/dev/"):
            issues.append("disk path must be an absolute /dev/... path")
        if self.confirm_disk != self.disk_path:
            issues.append("confirmation disk path does not match the selected disk")
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
        if self.root_mib is not None and int(self.root_mib) < 8192:
            issues.append("root must be at least 8192 MiB")
        if self.esp_mib < 32 or self.esp_mib > 4096:
            issues.append("ESP size must be between 32 and 4096 MiB")
        if self.swap_mib is not None and int(self.swap_mib) < 0:
            issues.append("swap size must not be negative")
        if len(set(self.delete_partitions)) != len(self.delete_partitions):
            issues.append("delete_partitions contains duplicates")
        if any(int(n) < 1 for n in self.delete_partitions):
            issues.append("delete_partitions entries must be positive")
        if not os.path.isabs(self.repo):
            issues.append("repo path must be absolute")
        if not os.path.isabs(self.target):
            issues.append("target path must be absolute")
        return issues

    def public_dict(self) -> dict[str, Any]:
        return {
            "disk": {
                "path": self.disk_path,
                "serial": self.disk_serial,
                "size_bytes": self.disk_size_bytes,
                "model": self.disk_model,
            },
            "delete_partitions": list(self.delete_partitions),
            "region_start_mib": self.region_start_mib,
            "esp_mib": self.esp_mib,
            "root_mib": self.root_mib,
            "swap_mib": self.swap_mib,
            "package_set": self.package_set,
            "hostname": self.hostname,
            "admin": {"username": self.admin_user, "password": "<redacted>"},
            "repo": self.repo,
            "target": self.target,
            "dry_run": self.dry_run,
        }

    @classmethod
    def from_mapping(
        cls,
        data: dict[str, Any],
        *,
        repo: str = "/run/initramfs/live/repo",
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
        version = data.get("version", 1)
        if version != 1:
            raise ConfigError(f"unsupported answer-file version: {version!r}")
        disk_data = data.get("disk")
        if not isinstance(disk_data, dict):
            raise ConfigError("answer file has no disk object")
        unknown_disk = set(disk_data) - _DISK_KEYS
        if unknown_disk:
            raise ConfigError(
                "unknown disk keys: " + ", ".join(sorted(unknown_disk))
            )
        path = disk_data.get("path")
        if not isinstance(path, str):
            raise ConfigError("disk.path must be a string")
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
        delete = data.get("delete_partitions") or []
        if not isinstance(delete, list) or any(
            not isinstance(item, int) or isinstance(item, bool) for item in delete
        ):
            raise ConfigError("delete_partitions must be a list of integers")
        region = data.get("region")
        region_start_mib: int | None = None
        if region is not None:
            if not isinstance(region, dict):
                raise ConfigError("region must be null or an object")
            unknown_region = set(region) - {"start_mib", "start"}
            if unknown_region:
                raise ConfigError(
                    "unknown region keys: " + ", ".join(sorted(unknown_region))
                )
            if "start_mib" in region:
                region_start_mib = int(region["start_mib"])
            elif "start" in region:
                # Historically a sector value; accept it only as MiB for now.
                region_start_mib = int(region["start"]) // 2048
            else:
                raise ConfigError("region needs start_mib")
        size = disk_data.get("size_bytes")
        root_mib = data.get("root_mib")
        swap_mib = data.get("swap_mib", 2048)
        config = cls(
            disk_path=path,
            disk_serial=disk_data.get("serial"),
            disk_size_bytes=int(size) if size is not None else None,
            disk_model=disk_data.get("model"),
            delete_partitions=tuple(int(n) for n in delete),
            region_start_mib=region_start_mib,
            esp_mib=int(data.get("esp_mib", 512)),
            root_mib=int(root_mib) if root_mib is not None else None,
            swap_mib=int(swap_mib) if swap_mib is not None else None,
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
        plan: LayoutPlan,
        *,
        on_step: Callable[[int, int, str], None] | None = None,
        on_line: Callable[[str], None] | None = None,
    ) -> None:
        self.config = config
        self.runner = runner
        self.logger = logger
        self.probe = probe
        self.plan = plan
        self.on_step = on_step
        self.on_line = on_line
        self.kver = FALLBACK_KVER
        self.current_step = ""
        self.root_mounted = False
        self.esp_mounted = False
        self.bind_mounted = False
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
            Step("repo", "Copying the package repository"),
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
            disk=self.plan.disk_path,
            table=self.plan.to_dict(),
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
            self.logger.info("install-complete", disk=self.plan.disk_path)
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
        self.logger.plan(self.plan.to_dict())
        # 1. Snapshot.  A failure here is safe: nothing has changed yet.
        for command in disk.snapshot_commands(self.plan, self.backup_dir):
            self._run(command)
        # 2. Delete selected entries and write the full replacement table.
        try:
            for command in disk.delete_commands(self.plan):
                self._run(command)
            for command in disk.write_table_commands(self.plan):
                self._run(command)
        except CommandError as exc:
            self.logger.error("partition-write-failed", error=str(exc))
            self._rollback("partition table write failed")
            raise InstallError(
                "partition",
                "writing the replacement partition table failed: {}".format(exc),
                reversible=True,
                remedy="the saved table was restored",
            ) from exc

        self.destructive_started = True

        if self.runner.dry_run:
            self.logger.info("partition-plan-recorded")
            return

        probed = self.probe.find_disk(self.plan.disk_path, refresh=True)
        if probed is None:
            self._rollback("selected disk disappeared")
            raise InstallError(
                "partition",
                "the selected disk is no longer present",
                reversible=True,
            )
        after = self.probe.read_table(probed.disk)
        issues = disk.verify_preserved(
            self.plan.table,
            after,
            self.plan.delete_numbers,
            self.plan.allowed_new_numbers,
        )
        issues.extend(disk.verify_planned(self.plan, after))
        if issues:
            self.logger.error("partition-verify-failed", issues=issues)
            self._rollback("partition preservation check failed")
            raise InstallError(
                "partition",
                "the new partition table did not preserve existing entries: "
                + "; ".join(issues),
                reversible=True,
                remedy="the saved table was restored; no filesystem was written",
            )
        self.logger.info("partition-verified", table=after)

    def _rollback(self, reason: str) -> None:
        if self.runner.dry_run:
            return
        self.logger.warning("rollback-start", reason=reason)
        try:
            for command in disk.rollback_commands(self.plan, self.backup_dir):
                self._run(command)
            self.logger.info("rollback-done")
        except CommandError as exc:
            self.logger.error("rollback-failed", error=str(exc))

    def step_format(self) -> None:
        if not self.runner.dry_run and not self.probe.wait_for_partuuid(self.plan):
            raise InstallError(
                "format",
                "the new partition device nodes did not appear (udev did not settle)",
                reversible=True,
            )
        for command in disk.format_commands(self.plan):
            self._run(command)
        self.destructive_started = True
        if self.runner.dry_run:
            self.logger.info("format-plan-recorded")
            return
        expected = {
            "esp-type": "vfat",
            "root-type": "ext4",
        }
        results = [self._run(c) for c in disk.format_verify_commands(self.plan)]
        values = [r.output.strip() for r in results]
        if len(values) >= 4:
            esp_type, esp_uuid, root_type, root_uuid = values[:4]
            if esp_type.lower() != expected["esp-type"]:
                raise InstallError(
                    "format",
                    f"ESP is {esp_type!r}, expected vfat",
                    reversible=False,
                )
            if root_type.lower() != expected["root-type"]:
                raise InstallError(
                    "format",
                    f"root is {root_type!r}, expected ext4",
                    reversible=False,
                )
            if self.plan.esp.fs_uuid and esp_uuid.upper() != self.plan.esp.fs_uuid.upper():
                raise InstallError(
                    "format",
                    "ESP UUID mismatch: {} != {}".format(
                        esp_uuid, self.plan.esp.fs_uuid
                    ),
                    reversible=False,
                )
            if self.plan.root.fs_uuid and root_uuid.lower() != self.plan.root.fs_uuid.lower():
                raise InstallError(
                    "format",
                    "root UUID mismatch: {} != {}".format(
                        root_uuid, self.plan.root.fs_uuid
                    ),
                    reversible=False,
                )
        # A read-only filesystem check is informative, not a hard failure right
        # after mkfs.  Do it so a broken image is visible in the log.
        self.runner.run(
            ("fsck.fat", "-n", self.probe.resolve_partition(self.plan.esp)),
            step="format",
            read_only=True,
            destructive=False,
            allow_failure=True,
            description="check the new ESP",
        )
        self.runner.run(
            ("e2fsck", "-fn", self.probe.resolve_partition(self.plan.root)),
            step="format",
            read_only=True,
            destructive=False,
            allow_failure=True,
            description="check the new root filesystem",
        )

    def step_mount(self) -> None:
        root_dev = self.probe.resolve_partition(self.plan.root)
        esp_dev = self.probe.resolve_partition(self.plan.esp)
        self.runner.makedirs(self.target, step="mount")
        self.runner.run(
            ("mount", "-o", "rw,noatime", root_dev, self.target),
            step="mount",
            description="mount the new root filesystem",
        )
        self.root_mounted = True
        self.runner.makedirs(os.path.join(self.target, "boot", "efi"), step="mount")
        self.runner.run(
            (
                "mount",
                "-o",
                "rw,umask=0077",
                esp_dev,
                os.path.join(self.target, "boot", "efi"),
            ),
            step="mount",
            description="mount the EFI System Partition",
        )
        self.esp_mounted = True
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
                description="mount efivarfs for grub-install",
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
        argv = [
            "dnf",
            "-y",
            "--nogpgcheck",
            "--installroot",
            self.target,
            "--releasever=" + RELEASEVER,
            "--disablerepo=*",
            "--repofrompath=browneye,file://" + self.config.repo,
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

    def step_repo(self) -> None:
        """Keep the install media's repository on the target.

        The installed system can then dnf install packages offline
        (opencode, herdr, build tooling) without the original ISO.
        """
        live_repo = "/run/initramfs/live/repo"
        if not os.path.isdir(live_repo):
            self.logger.warning(
                "repo-copy-skipped", reason="no repository on the install media")
            return

        base = os.path.join(self.target, "var", "lib", "browneye")
        dest = os.path.join(base, "repo")
        repos_dir = os.path.join(self.target, "etc", "yum.repos.d")
        self.runner.run(
            ("install", "-dm0755", base, dest, repos_dir),
            step="repo", description="create the local repository directory")
        self.runner.run(
            ("cp", "-a", live_repo + "/.", dest + "/"),
            step="repo", description="copy the install repository",
            timeout=1800)
        self.runner.write_file(
            os.path.join(repos_dir, "browneye-local.repo"),
            "[browneye-local]\n"
            "name=Browneye Linux 13.1 (install media)\n"
            "baseurl=file:///var/lib/browneye/repo\n"
            "enabled=1\n"
            "gpgcheck=0\n"
            "repo_gpgcheck=0\n"
            "skip_if_unavailable=1\n",
            step="repo",
        )

    def step_configure(self) -> None:
        self._write_fstab()
        self._write_network_files()
        self._configure_systemd()
        self._configure_users()

    def _uuid_ref(self, part: disk.PlannedPartition) -> str:
        if part.fs_uuid:
            return "UUID=" + part.fs_uuid
        return "PARTUUID=" + part.partuuid

    def _write_fstab(self) -> None:
        lines = [
            "# <file system> <mount point> <type> <options> <dump> <pass>",
            "{} / ext4 defaults,noatime 0 1".format(self._uuid_ref(self.plan.root)),
            "{} /boot/efi vfat umask=0077,shortname=winnt 0 2".format(
                self._uuid_ref(self.plan.esp)
            ),
        ]
        if self.plan.swap is not None:
            lines.append(
                "{} none swap sw 0 0".format(self._uuid_ref(self.plan.swap))
            )
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
        self.runner.run(
            (
                "chroot",
                self.target,
                "/usr/bin/grub-install",
                "--target=x86_64-efi",
                "--efi-directory=/boot/efi",
                "--boot-directory=/boot",
                "--bootloader-id=browneye",
                "--recheck",
                "--no-nvram",
            ),
            step="bootloader",
            description="install GRUB for x86_64-efi without touching NVRAM",
        )
        self.runner.write_file(
            os.path.join(self.target, "boot", "grub", "grub.cfg"),
            self._grub_cfg(),
            mode=0o644,
            step="bootloader",
        )
        source = os.path.join(
            self.target, "boot", "efi", "EFI", "browneye", "grubx64.efi"
        )
        destination = os.path.join(
            self.target, "boot", "efi", "EFI", "BOOT", "BOOTX64.EFI"
        )
        self.runner.run(
            ("install", "-D", "-m", "0644", source, destination),
            step="bootloader",
            description="install the removable EFI/BOOT/BOOTX64.EFI fallback",
        )
        if not self.runner.dry_run:
            if not os.path.isfile(source):
                raise InstallError(
                    "bootloader",
                    "grub-install did not create EFI/browneye/grubx64.efi",
                    reversible=False,
                )
            if not os.path.isfile(destination):
                raise InstallError(
                    "bootloader",
                    "the removable BOOTX64.EFI fallback was not installed",
                    reversible=False,
                )
        loader = r"\EFI\browneye\grubx64.efi"
        self.runner.run(
            (
                "efibootmgr",
                "--create",
                "--disk",
                self.plan.disk_path,
                "--part",
                str(self.plan.esp.number),
                "--label",
                "Browneye Linux",
                "--loader",
                loader,
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

    def _grub_cfg(self) -> str:
        root_ref = self._uuid_ref(self.plan.root)
        root_uuid = self.plan.root.fs_uuid or ""
        lines = [
            "set timeout=5",
            "set default=0",
            "",
            "menuentry 'Browneye Linux 13.1' {",
            "    insmod part_gpt",
            "    insmod fat",
            "    insmod ext2",
        ]
        if root_uuid:
            lines.append(
                "    search --no-floppy --fs-uuid --set=root " + root_uuid
            )
        lines.extend(
            [
                "    linux /boot/vmlinuz-{} root={} ro rootwait".format(
                    self.kver, root_ref
                ),
                "    initrd /boot/initramfs-{}.img".format(self.kver),
                "}",
                "",
            ]
        )
        return "\n".join(lines)

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
        esp = os.path.join(self.target, "boot", "efi")
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
            esp = os.path.join(self.target, "boot", "efi")
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
        mountpoint = "/run/browneye/esp-failure"
        self.runner.makedirs(mountpoint, step="failure", allow_failure=True)
        mounted = self.runner.run(
            (
                "mount",
                "-o",
                "rw,umask=0077",
                self.plan.esp.by_partuuid,
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
