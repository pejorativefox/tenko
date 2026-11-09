"""Command line entry point and screen flow for tenko-installer."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, replace
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

VERSION = "6"
DEFAULT_REPO = "https://tenko.pjfox.xyz/packages/6/"
DEFAULT_TARGET = "/mnt/tenko"
LOG_DIR = "/run/tenko"
LOG_JSONL = os.path.join(LOG_DIR, "install.jsonl")
PLAN_JSON = os.path.join(LOG_DIR, "plan.json")
ANSWER_PATHS = (
    "/run/initramfs/live/answer.json",
    "/sys/firmware/qemu_fw_cfg/by_name/opt/tenko/answer.json/raw",
    "/dev/disk/by-label/TENKO-ANSWER/answer.json",
)
MIB = 1024 * 1024
GIB = 1024 * MIB
NETWORK_TOOL_PATH = "/usr/sbin:/usr/bin:/sbin:/bin"
REPOSITORY_CHECK = "package repository"


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
    line = "TENKO-INSTALL: " + text
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
    """Write /run/tenko/probe.json for post-mortem debugging."""

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
        if token.startswith("tenko.answer="):
            result["answer"] = token.split("=", 1)[1]
        elif token in ("tenko.auto=1", "tenko.auto=true"):
            result["auto"] = True
        elif token in ("tenko.console=serial", "tenko.serial=1"):
            result["serial"] = True
        elif token in ("tenko.dry_run=1", "tenko.dry-run=1"):
            result["dry_run"] = True
        elif token in ("tenko.debug=1", "tenko.debug=true"):
            result["debug"] = True
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="tenko-installer",
        description="Install Tenko Linux 6 (Workstation) on a GPT disk.",
    )
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument(
        "--repo",
        default=None,
        help="RPM repository, URL or path (default: the Tenko 6 repository)",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="installation mount point (default: /mnt/tenko)",
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


ANSWER_LABEL = "/dev/disk/by-label/TENKO-ANSWER"
ANSWER_MOUNT = "/run/tenko/answer"


def mount_answer_disk() -> str | None:
    """Mount a TENKO-ANSWER medium read-only and return its answer.json.

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
    *,
    repo_attempts: int = 6,
) -> tuple[list[Check], bool]:
    live_kname = probe.detect_live_disk(refresh=True)
    checks = probe.preflight(
        repo=config.repo,
        target=config.target,
        live_kname=live_kname,
        dry_run=config.dry_run,
        repo_attempts=repo_attempts,
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


# ---------------------------------------------------------------------------
# Network setup
# ---------------------------------------------------------------------------


def repository_check_failed(checks: Sequence[Check]) -> bool:
    """True when the package repository check failed."""

    return any(
        not check.ok and check.label == REPOSITORY_CHECK for check in checks
    )


def _nmcli_command(runner: CommandRunner, *argv: str) -> str:
    if shutil.which(argv[0], path=NETWORK_TOOL_PATH) is None:
        return ""
    try:
        result = runner.run(
            argv,
            step="network",
            read_only=True,
            destructive=False,
            allow_failure=True,
            timeout=10,
            description="read the network state",
        )
    except (CommandError, OSError):
        return ""
    return result.output


def _split_nmcli_fields(line: str) -> list[str]:
    """Split nmcli's terse output, which escapes ':' as '\\:'."""

    fields: list[str] = []
    current: list[str] = []
    escaped = False
    for char in line:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == ":":
            fields.append("".join(current))
            current = []
        else:
            current.append(char)
    fields.append("".join(current))
    return fields


def network_status_lines(runner: CommandRunner) -> list[str]:
    """A short, readable device list for the network setup screen."""

    output = _nmcli_command(
        runner,
        "nmcli",
        "-t",
        "-f",
        "DEVICE,TYPE,STATE,CONNECTION",
        "device",
        "status",
    )
    lines: list[str] = []
    for raw in output.splitlines():
        fields = _split_nmcli_fields(raw)
        if len(fields) < 3:
            continue
        device, type_name, state = fields[:3]
        connection = fields[3] if len(fields) > 3 else ""
        text = "{:<12} {:<10} {:<12}".format(device, type_name, state)
        if connection:
            text += "  " + connection
        lines.append(text.rstrip())
    if lines:
        return lines
    if shutil.which("nmcli", path=NETWORK_TOOL_PATH) is None:
        return ["NetworkManager (nmcli) is not installed."]
    if not output:
        return ["NetworkManager returned no devices."]
    return output.splitlines()[:8]


def launch_nmtui(
    runner: CommandRunner,
    logger: Logger,
    ui: CursesUI | None = None,
) -> bool:
    """Run nmtui in the foreground, suspending curses while it owns the tty."""

    program = shutil.which(
        "nmtui-connect", path=NETWORK_TOOL_PATH
    ) or shutil.which("nmtui", path=NETWORK_TOOL_PATH)
    if program is None:
        logger.warning("network-setup-unavailable", program="nmtui")
        return False

    logger.info("network-setup", program=program)
    suspended = False
    if ui is not None:
        try:
            curses.def_prog_mode()
            curses.endwin()
            suspended = True
        except curses.error:
            suspended = False
    try:
        env = runner.env.copy()
        env.setdefault("TERM", os.environ.get("TERM", "linux"))
        subprocess.run((program,), env=env, check=False)
    except OSError as exc:
        logger.warning("network-setup-failed", error=str(exc))
        return False
    finally:
        if suspended and ui is not None:
            try:
                curses.reset_prog_mode()
            except curses.error:
                pass
            try:
                ui.screen.clear()
                ui.screen.refresh()
            except curses.error:
                pass
    return True


def network_setup_screen(
    ui: CursesUI,
    runner: CommandRunner,
    logger: Logger,
) -> bool:
    """Offer nmtui and a retry; return True when the caller should retry."""

    while True:
        status = network_status_lines(runner)
        rows = [
            Row("Connect a network (nmtui)"),
            Row("Retry the network check"),
            Row("Exit the installer", note="Ctrl+Alt+F2 gives a shell"),
        ]
        choice = ui.menu(
            "Network required",
            "Tenko downloads every package from the repository; no usable "
            "network connection was found.",
            rows,
            footer="Up/Down select   Enter continue",
            allow_rescan=False,
            detail=lambda _index: status,
            detail_height=min(10, max(2, len(status))),
        )
        if choice in (QUIT, 2):
            return False
        if choice == 1:
            return True
        if not launch_nmtui(runner, logger, ui=ui):
            ui.message(
                "Network setup is unavailable",
                [
                    "nmtui was not found on this live medium.",
                    "",
                    "Use wired Ethernet, a USB Ethernet adapter or USB",
                    "tethering, then choose Retry.",
                ],
                footer="Press any key to continue",
            )
            continue
        # Return to the caller, which immediately probes the repository again.
        return True


def plain_network_retry(
    probe: Probe,
    config: InstallConfig,
    logger: Logger,
    runner: CommandRunner,
    checks: list[Check],
    ok: bool,
) -> tuple[list[Check], bool]:
    """Line-oriented equivalent of the network setup screen."""

    while not ok and repository_check_failed(checks):
        print(
            "\nThe installer downloads packages from {}; the network is "
            "not reachable.".format(config.repo)
        )
        print("Connect a network (for example Wi-Fi with nmtui) and retry.")
        for line in network_status_lines(runner):
            print("  " + line)
        answer = _ask("Run nmtui now? (y/N, or q to exit)", "")
        if answer.lower() in ("q", "quit"):
            break
        if answer.lower() in ("y", "yes"):
            if not launch_nmtui(runner, logger):
                print("nmtui is not available on this live medium.")
                break
        else:
            answer = _ask(
                "Press Enter to retry the network check, or q to exit", ""
            )
            if answer.lower() in ("q", "quit"):
                break
        checks, ok = run_preflight(probe, config, logger, repo_attempts=2)
        for check in checks:
            print(
                "  [{}] {}: {}".format(
                    "ok" if check.ok else "!!", check.label, check.detail
                )
            )
    return checks, ok


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

_V3_KEYS = {
    "version",
    "mode",
    "disk",
    "filesystem",
    "swap",
    "swap_mib",
    "encrypt",
    "package_set",
    "hostname",
    "timezone",
    "locale",
    "keymap",
    "admin",
    "confirm",
    "dry_run",
}


def _config_from_v3(
    data: dict[str, Any], args: argparse.Namespace, probe: Probe
) -> InstallConfig:
    """Build an InstallConfig from the guided (version 3) answer form."""
    unknown = set(data) - _V3_KEYS
    if unknown:
        raise ConfigError(
            "unknown answer-file keys: " + ", ".join(sorted(unknown))
        )
    if data.get("encrypt"):
        raise ConfigError(
            "encryption is not implemented yet; remove 'encrypt' or set it to false"
        )
    mode = str(data.get("mode", ""))
    if mode not in ("erase-disk", "free-space"):
        raise ConfigError("mode must be 'erase-disk' or 'free-space'")
    disk_path = str(data.get("disk", ""))
    if not disk_path.startswith("/dev/"):
        raise ConfigError("disk must be a /dev/ path")
    fstype = str(data.get("filesystem", "ext4"))
    swap = str(data.get("swap", "swapfile"))
    if swap not in ("swapfile", "partition", "none"):
        raise ConfigError("swap must be 'swapfile', 'partition' or 'none'")
    swap_mib = data.get("swap_mib", layout_module.SWAP_MIB)
    if isinstance(swap_mib, bool) or not isinstance(swap_mib, int):
        raise ConfigError("swap_mib must be an integer")

    probed = probe.probe_disks(refresh=True)
    item = next((entry for entry in probed if entry.name == disk_path), None)
    if item is None or item.table is None:
        raise ConfigError(
            "disk {} was not found or cannot be partitioned".format(disk_path)
        )
    layout_swap = "partition" if swap == "partition" else "none"
    try:
        if mode == "erase-disk":
            spec = layout_module.plan_erase_disk(
                item.table, fstype=fstype, swap=layout_swap, swap_mib=swap_mib
            )
        else:
            spec = layout_module.plan_free_space(
                item.table, fstype=fstype, swap=layout_swap, swap_mib=swap_mib
            )
    except (ValueError, disk.PlanError) as exc:
        raise ConfigError(str(exc)) from exc
    spec = replace(
        spec,
        path=item.disk.path,
        serial=item.disk.serial,
        size_bytes=item.disk.size_bytes,
        model=item.disk.model,
    )

    admin = data.get("admin")
    if not isinstance(admin, dict):
        raise ConfigError("answer file has no admin object")
    confirm = data.get("confirm")
    if not isinstance(confirm, dict):
        raise ConfigError("answer file has no confirm object")

    return InstallConfig(
        layout=InstallSpec(disks=(spec,)),
        package_set=str(data.get("package_set", "desktop")),
        hostname=str(data.get("hostname", "tenko")),
        timezone=str(data.get("timezone", "UTC")),
        locale=str(data.get("locale", "C.UTF-8")),
        keymap=str(data.get("keymap", "us")),
        admin_user=str(admin.get("username", "admin")),
        admin_password=str(admin.get("password", "")),
        confirm_disk=str(confirm.get("disk", disk_path)),
        confirm_phrase=str(confirm.get("phrase", "")),
        repo=args.repo,
        target=args.target,
        dry_run=args.dry_run or bool(data.get("dry_run", False)),
        swap_mode=swap,
        swap_mib=swap_mib,
    )


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
        if data.get("version") == 3:
            config = _config_from_v3(data, args, probe)
        else:
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
        if repository_check_failed(checks):
            marker(
                "HINT network: run nmtui-connect, then rerun the installer"
            )
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
    checks, ok = run_preflight(probe, preflight_config, logger, repo_attempts=1)
    for check in checks:
        print("  [{}] {}: {}".format("ok" if check.ok else "!!", check.label, check.detail))
    if not ok and repository_check_failed(checks):
        checks, ok = plain_network_retry(
            probe, preflight_config, logger, runner, checks, ok
        )
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

    hostname = _ask("Hostname", "tenko")
    timezone = _ask("Timezone (IANA name)", "UTC")
    locale = _ask("Locale", "C.UTF-8")
    keymap = _ask("Keymap", "us")
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
        timezone=timezone,
        locale=locale,
        keymap=keymap,
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


def _parse_size_mib(value: str, *, what: str = "size") -> int | None:
    """Parse ``20``, ``20G``, ``20GiB`` or ``512M`` into MiB.

    A bare number is GiB, matching the label shown by the forms.  The
    planner still works in MiB internally.
    """

    text = value.strip().lower().replace(" ", "")
    if not text:
        return None
    match = re.fullmatch(r"(\d+(?:\.\d+)?)([kmgt]i?b?)?", text)
    if match is None:
        raise ValueError(
            "{} must be a number, optionally followed by M, G, MiB or GiB".format(
                what
            )
        )
    number = float(match.group(1))
    suffix = (match.group(2) or "g").rstrip("b")
    factor = {
        "": 1024,
        "k": 1 / 1024,
        "ki": 1 / 1024,
        "m": 1,
        "mi": 1,
        "g": 1024,
        "gi": 1024,
        "t": 1024 * 1024,
        "ti": 1024 * 1024,
    }.get(suffix)
    if factor is None:
        raise ValueError("{} has an unknown unit".format(what))
    mib = int(round(number * factor))
    if mib <= 0:
        raise ValueError("{} must be positive".format(what))
    return mib


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
            role="root",
            fstype="ext4",
            mountpoint="/",
        )
    )
    return DiskSpec(partitions=tuple(specs), **base)


def _partition_label(part: disk.Partition) -> str:
    fstype = (part.fstype or "").lower()
    if (part.type or "").upper() == disk.ESP_TYPE:
        return "ESP"
    if fstype in ("ntfs", "fat", "fat32", "msdos"):
        return "Windows"
    if fstype == "swap":
        return "swap"
    if part.name:
        return part.name
    if fstype:
        return fstype
    return disk.type_name(part.type, False)


def _disk_map_lines(
    table: PartitionTable,
    width: int,
    *,
    delete_numbers: Sequence[int] = (),
) -> list[str]:
    """Render a proportional one-line map plus a size legend."""

    width = max(24, width)
    total = table.total_sectors or 1
    unit = table.unit or 512
    parts = sorted(table.partitions, key=lambda part: part.number)
    segments: list[tuple[int, str]] = []
    used = 0
    for part in parts:
        used += part.size
        label = _partition_label(part)
        if part.number in delete_numbers:
            label = "delete " + label
        segments.append((part.size, label))
    free = max(0, total - used)
    if free:
        segments.append((free, "free"))
    if not segments:
        return []

    inner = max(10, width - len(segments) - 1)
    widths = [
        max(3, int(round(inner * size / total)))
        for size, _label in segments
    ]
    while sum(widths) > inner:
        index = max(range(len(widths)), key=lambda item: widths[item])
        if widths[index] <= 3:
            break
        widths[index] -= 1
    while sum(widths) < inner:
        index = max(range(len(widths)), key=lambda item: widths[item])
        widths[index] += 1

    cells = []
    for cell_width, (_size, label) in zip(widths, segments):
        if len(label) > cell_width:
            label = label[: max(1, cell_width - 1)] + "~"
        cells.append(label.center(cell_width))
    bar = "|" + "|".join(cells) + "|"
    legend = "  ".join(
        "{} {}".format(
            label, disk.human_size(size * unit)
        )
        for size, label in segments
    )
    return [bar[:width], legend[:width]]


def _select_disks(
    ui: CursesUI, probed: Sequence[ProbedDisk]
) -> list[ProbedDisk] | None:
    selected: list[str] = []
    while True:
        rows: list[Row] = []
        for item in probed:
            status = "selectable" if item.selectable else "; ".join(item.reasons)
            note = status
            if item.disk.path in selected:
                root = selected.index(item.disk.path) == 0
                note = "root disk" if root else "additional disk"
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
                    note=note,
                )
            )
        rows.append(Row("Continue with these disks"))

        def detail(index: int) -> Sequence[str]:
            if 0 <= index < len(probed):
                table = probed[index].table
                if table is not None:
                    return _disk_map_lines(table, ui.cols - 8)
            return []

        choice = ui.menu(
            "Select installation disks",
            "The first disk you select becomes the root disk. Press Enter "
            "to toggle a disk or to continue.",
            rows,
            footer="Up/Down select   Enter toggle/continue   r rescan   q quit",
            allow_back=True,
            detail=detail,
            detail_height=2,
        )
        if choice in (QUIT, BACK):
            return None
        if choice == RESCAN:
            return []
        if choice == len(rows) - 1:
            chosen = [
                item for item in probed if item.disk.path in selected
            ]
            chosen.sort(key=lambda item: selected.index(item.disk.path))
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
            selected.append(item.disk.path)


def _existing_row(part: disk.Partition, table: PartitionTable) -> str:
    text = "{}  start {}  size {}  {}".format(
        part.number,
        disk.human_size(part.start * table.unit),
        disk.human_size(part.size * table.unit),
        disk.type_name(part.type, table.is_mbr),
    )
    if part.fstype:
        text += "  " + part.fstype
    if part.name:
        text += "  " + part.name
    return text


def _add_partition_form(ui: CursesUI) -> PartitionSpec | None:
    mount_value = ""
    fstype_value = "ext4"
    size_value = ""
    region_value = ""
    name_value = ""
    while True:
        values = ui.form(
            "New partition",
            [
                Field("Mount point (blank = swap)", mount_value),
                Field("Filesystem (ext4/btrfs/vfat/swap)", fstype_value),
                Field("Size (GiB, blank = fill region)", size_value),
                Field("Region start (GiB, blank = auto)", region_value),
                Field("Name (optional)", name_value),
            ],
            subtitle="A mount point of / makes the partition root; /boot makes it the ESP.",
            footer="Tab next   Enter continue   Esc back",
        )
        if values is None:
            return None
        mount, fstype, size_text, region_text, name = [
            value.strip() for value in values
        ]
        mount_value, fstype_value = mount, fstype
        size_value, region_value, name_value = size_text, region_text, name
        if not mount and fstype != "swap":
            ui.message(
                "Mount point required",
                ["A mount point is required unless the filesystem is swap."],
                footer="Press any key to retry",
            )
            continue
        role = _role_for(mount, fstype)
        if role == "esp":
            fstype = "vfat"
            mount = "/boot"
        elif role == "swap":
            fstype = "swap"
            mount = ""
        try:
            size_mib = _parse_size_mib(size_text, what="size")
            region_start = _parse_size_mib(
                region_text, what="region start"
            )
        except ValueError as exc:
            ui.message(
                "Invalid partition",
                [str(exc)],
                footer="Press any key to retry",
            )
            continue
        try:
            spec = PartitionSpec(
                role=role,
                fstype=fstype,
                mountpoint=mount or None,
                size_mib=size_mib,
                region_start_mib=region_start,
                name=name or None,
            )
        except ValueError:
            ui.message(
                "Invalid partition",
                ["Sizes and region starts must be numbers."],
                footer="Press any key to retry",
            )
            continue
        issues = spec.validate()
        if issues:
            ui.message("Invalid partition", issues, footer="Press any key to retry")
            continue
        return spec


def _assign_existing_form(
    ui: CursesUI, table: PartitionTable, *, number: int | None = None
) -> PartitionSpec | None:
    number_value = "" if number is None else str(number)
    mount_value = ""
    format_value = "n"
    fstype_value = ""
    while True:
        fields = [
            Field("Mount point (blank = use as swap)", mount_value),
            Field("Format it? (y/N)", format_value),
            Field("Filesystem when formatting (blank = keep)", fstype_value),
        ]
        if number is None:
            fields.insert(0, Field("Partition number", number_value))
        values = ui.form(
            "Assign an existing partition",
            fields,
            subtitle="Leave format off to keep the existing data and filesystem.",
            footer="Tab next   Enter continue   Esc back",
        )
        if values is None:
            return None
        if number is None:
            number_text, mountpoint, format_text, fstype_text = [
                value.strip() for value in values
            ]
            number_value = number_text
        else:
            mountpoint, format_text, fstype_text = [
                value.strip() for value in values
            ]
        mount_value, format_value, fstype_value = (
            mountpoint,
            format_text,
            fstype_text,
        )
        try:
            selected = int(number_text) if number is None else number
        except ValueError:
            ui.message(
                "Invalid number",
                ["The partition number must be an integer."],
                footer="Press any key to retry",
            )
            continue
        part = table.find_number(int(selected or 0))
        if part is None:
            ui.message(
                "No such partition",
                ["Partition {} does not exist.".format(selected)],
                footer="Press any key to retry",
            )
            continue
        format_existing = format_text.lower() in ("y", "yes")
        detected = _fs_for_existing(part)
        fstype = fstype_text.lower() or detected
        if not format_existing:
            if not detected:
                ui.message(
                    "Unknown filesystem",
                    [
                        "Partition {} has no readable filesystem.".format(
                            selected
                        ),
                        "Enable formatting or create a new partition instead.",
                    ],
                    footer="Press any key to retry",
                )
                continue
            fstype = detected
        if not mountpoint and fstype != "swap":
            ui.message(
                "Mount point required",
                [
                    "Partition {} is not swap; enter a mount point.".format(
                        selected
                    )
                ],
                footer="Press any key to retry",
            )
            continue
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
            continue
        spec = PartitionSpec(
            role=role,
            fstype=fstype,
            mountpoint=mountpoint or None,
            existing_number=int(selected or 0),
            format=format_existing,
        )
        issues = spec.validate()
        if issues:
            ui.message(
                "Invalid assignment", issues, footer="Press any key to retry"
            )
            continue
        return spec


def _pick_existing_partition(
    ui: CursesUI,
    table: PartitionTable,
    title: str,
    subtitle: str,
) -> disk.Partition | None:
    parts = sorted(table.partitions, key=lambda part: part.number)
    if not parts:
        ui.message(
            "No partitions",
            ["This disk has no existing partitions."],
            footer="Press any key to continue",
        )
        return None
    rows = [Row(_existing_row(part, table)) for part in parts]
    rows.append(Row("Cancel"))
    choice = ui.menu(
        title,
        subtitle,
        rows,
        footer="Up/Down select   Enter continue   Esc back",
        allow_back=True,
    )
    if choice in (BACK, QUIT) or choice == len(rows) - 1:
        return None
    return parts[choice]


def _partition_actions(
    ui: CursesUI,
    table: PartitionTable,
    part: disk.Partition,
    specs: list[PartitionSpec],
    delete_set: set[int],
) -> None:
    """Act on the partition the user selected, without typing its number."""

    while True:
        assigned = next(
            (
                spec
                for spec in specs
                if spec.existing_number == part.number
            ),
            None,
        )
        rows: list[Row] = []
        if part.number in delete_set:
            rows.append(
                Row("Keep this partition", note="cancel the deletion")
            )
        else:
            rows.append(
                Row(
                    "Assign or edit this partition",
                    note=(
                        "{} {}".format(
                            assigned.role, assigned.mountpoint or "swap"
                        )
                        if assigned is not None
                        else "not used by Tenko"
                    ),
                )
            )
            rows.append(
                Row("Delete this partition", note="entry is removed when applied")
            )
        rows.append(Row("Back"))
        choice = ui.menu(
            "Partition {} on {}".format(part.number, table.device),
            "{}  {}".format(
                _existing_row(part, table),
                "marked for deletion" if part.number in delete_set else "",
            ),
            rows,
            footer="Up/Down select   Enter act   Esc back",
            allow_back=True,
        )
        if choice in (BACK, QUIT):
            return
        if choice == len(rows) - 1:
            return
        if part.number in delete_set:
            delete_set.discard(part.number)
            return
        if choice == 0:
            spec = _assign_existing_form(
                ui, table, number=part.number
            )
            if spec is None:
                continue
            if spec.role in ("root", "esp") and any(
                existing.role == spec.role
                and existing.existing_number != spec.existing_number
                for existing in specs
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
            specs[:] = [
                existing
                for existing in specs
                if existing.existing_number != part.number
            ]
            specs.append(spec)
            return
        confirm = ui.menu(
            "Delete partition {}?".format(part.number),
            "The partition entry is removed when the plan is applied. "
            "Its data is not recoverable afterwards.",
            [Row("Yes, delete it"), Row("No, keep it")],
            footer="Up/Down select   Enter confirm   Esc cancel",
            allow_back=True,
        )
        if confirm == 0:
            specs[:] = [
                existing
                for existing in specs
                if existing.existing_number != part.number
            ]
            delete_set.add(part.number)
            return


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
        existing_parts = sorted(
            table.partitions, key=lambda value: value.number
        )
        for part in existing_parts:
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
        new_specs = [
            spec for spec in specs if spec.existing_number is None
        ]
        for spec in new_specs:
            rows.append(
                Row(
                    "NEW {}  {}".format(
                        spec.role,
                        disk.human_size(
                            (spec.size_mib or 0) * MIB
                        )
                        if spec.size_mib is not None
                        else "fill remaining space",
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
                Row("Mark a partition for deletion"),
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
            "{}".format(disk.human_size(region.size_mib * MIB))
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
            detail=lambda _index: _disk_map_lines(
                table, ui.cols - 8, delete_numbers=tuple(sorted(delete_set))
            ),
            detail_height=2,
        )
        if choice in (BACK, QUIT):
            return None
        if choice == RESCAN:
            refreshed = probe.find_disk(item.disk.path, refresh=True) or item
            item = refreshed
            table = refreshed.table or probe.read_table(refreshed.disk)
            continue
        if choice < actions:
            if choice < len(existing_parts):
                _partition_actions(
                    ui,
                    table,
                    existing_parts[choice],
                    specs,
                    delete_set,
                )
            else:
                spec = new_specs[choice - len(existing_parts)]
                picked = ui.menu(
                    "Planned partition",
                    "{}  {}  {}".format(
                        spec.role,
                        spec.fstype,
                        spec.mountpoint or "swap",
                    ),
                    [Row("Remove this planned partition"), Row("Back")],
                    footer="Up/Down select   Enter act   Esc back",
                    allow_back=True,
                )
                if picked == 0:
                    specs.remove(spec)
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
            part = _pick_existing_partition(
                ui,
                table,
                "Assign an existing partition",
                "Choose the partition to use, then set its mount point.",
            )
            if part is None:
                continue
            spec = _assign_existing_form(
                ui, table, number=part.number
            )
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
            part = _pick_existing_partition(
                ui,
                table,
                "Mark a partition for deletion",
                "The partition entry is removed when the plan is applied.",
            )
            if part is None:
                continue
            number = part.number
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
                            disk.human_size(spec.size_mib * MIB)
                            if spec.size_mib is not None
                            else "fill remaining space"
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
        status = "modified" if item.changed else "not modified"
        if item.delete_numbers:
            status += ", {} deletion(s)".format(len(item.delete_numbers))
        lines.append("  {} ({})".format(item.disk_path, status))
        for part in item.table.partitions:
            if part.number in item.delete_numbers:
                lines.append(
                    "    delete {:>3}  {}".format(
                        part.number,
                        "{}  {}".format(
                            disk.human_size(part.size * item.unit),
                            disk.type_name(part.type, item.table.is_mbr),
                        ),
                    )
                )
        for part in item.partitions:
            label = part.mountpoint or "swap"
            lines.append(
                "    {} {:>4}  {}".format(
                    "keep" if part.existing and not part.format else "new ",
                    str(part.number),
                    "{}  {}  {}".format(
                        disk.human_size(part.size * item.unit),
                        part.fstype,
                        label,
                    ),
                )
            )
    swaps = [
        part for item in plan.disks for part in item.swaps
    ]
    if swaps:
        swap_text = "{} partition(s)".format(len(swaps))
    elif config.swap_mode == "swapfile":
        swap_text = "{} swapfile".format(
            disk.human_size(config.swap_mib * MIB)
        )
    else:
        swap_text = "none"
    lines.append("Swap: {}".format(swap_text))
    lines.append(
        "Account: {} on {}".format(config.admin_user, config.hostname)
    )
    lines.append(
        "Locale: {} · {} · {}".format(
            config.timezone, config.locale, config.keymap
        )
    )
    lines.append("Boot: systemd-boot on the ESP")
    lines.extend(
        [
            "Install: {}".format(", ".join(config.packages)),
            "",
        ]
    )
    deletions = sum(
        len(item.delete_numbers) for item in plan.disks
    )
    if deletions:
        lines.append(
            "This ERASES {} existing partition{}.".format(
                deletions, "" if deletions == 1 else "s"
            )
        )
    else:
        lines.append("No existing partition is deleted.")
    lines.append(
        "Other partitions are preserved. There is no undo after formatting."
    )
    for warning in config.warnings:
        lines.append("Warning: " + warning)
    return lines


def _free_space_text(table: PartitionTable) -> str:
    regions = layout_module.free_regions(table)
    if not regions:
        return "no free space"
    total = sum(region.size_mib for region in regions)
    return "{} free".format(disk.human_size(total * MIB))


def _install_mode(ui: CursesUI, simulated: bool) -> str | None:
    """Choose the guided or advanced flow."""

    rows = [
        Row(
            "Install Tenko Linux 6 (Workstation) (recommended)",
            note="guided: one disk, sensible defaults",
        ),
        Row(
            "Advanced installation",
            note="choose disks, partitions and mount points",
        ),
    ]
    choice = ui.menu(
        "Installation type"
        + (" (simulation)" if simulated else ""),
        "The guided install handles the common case. Use the advanced "
        "install to dual-boot, reuse partitions or spread the system "
        "across several disks.",
        rows,
        footer="Up/Down select   Enter continue   q quit",
        allow_back=False,
    )
    if choice in (QUIT, BACK):
        return None
    return "guided" if choice == 0 else "advanced"


def _guided_select_disk(
    ui: CursesUI, probe: Probe
) -> ProbedDisk | None:
    probed = probe.probe_disks(refresh=True)
    rows: list[Row] = []
    candidates: list[ProbedDisk] = []
    for item in probed:
        if not item.selectable:
            continue
        table = item.table or probe.read_table(item.disk)
        count = len(table.partitions)
        rows.append(
            Row(
                "{:<12} {:>9}  {:<24}".format(
                    item.disk.path,
                    disk.human_size(item.disk.size_bytes),
                    (item.disk.model or "")[:24],
                ),
                note="{} partition{}; {}".format(
                    count, "" if count == 1 else "s", _free_space_text(table)
                ),
            )
        )
        candidates.append(item)
    if not candidates:
        ui.message(
            "No selectable disk",
            [
                "No disk can be installed to.",
                "The live media, mounted disks, MBR disks and disks with",
                "holders or whole-disk filesystems are excluded.",
            ],
            footer="Press any key to exit",
        )
        return None
    rows.append(Row("Cancel"))

    def detail(index: int) -> Sequence[str]:
        if 0 <= index < len(candidates):
            table = candidates[index].table
            if table is not None:
                return _disk_map_lines(table, ui.cols - 8)
        return []

    choice = ui.menu(
        "Where to install",
        "Choose the disk that should receive Tenko Linux. "
        "Other disks are not touched.",
        rows,
        footer="Up/Down select   Enter continue   Esc back",
        allow_back=True,
        detail=detail,
        detail_height=2,
    )
    if choice in (BACK, QUIT) or choice == len(rows) - 1:
        return None
    return candidates[choice]


def _guided_mode(
    ui: CursesUI, table: PartitionTable
) -> str | None:
    regions = layout_module.free_regions(table)
    free_mib = sum(region.size_mib for region in regions)
    esp = layout_module.find_existing_esp(table)
    required = layout_module.ROOT_MIN_MIB
    if esp is None:
        required += layout_module.ESP_MIB
    can_use_free = free_mib >= required
    rows = [
        Row(
            "Erase the disk and install Tenko",
            note=(
                "deletes {} existing partition{}".format(
                    len(table.partitions),
                    "" if len(table.partitions) == 1 else "s",
                )
                if table.partitions
                else "blank disk"
            ),
        ),
        Row(
            "Use the free space (keep existing partitions)",
            enabled=can_use_free,
            note=(
                "{} free".format(disk.human_size(free_mib * MIB))
                if can_use_free
                else "needs at least {}".format(
                    disk.human_size(required * MIB)
                )
            ),
        ),
        Row(
            "Custom partitioning...",
            note="opens the advanced editor",
        ),
    ]
    choice = ui.menu(
        "Installation method",
        "Existing partitions are preserved unless you choose to erase the "
        "disk. Nothing is written until the review screen is confirmed.",
        rows,
        footer="Up/Down select   Enter continue   Esc back",
        allow_back=True,
        detail=lambda _index: _disk_map_lines(table, ui.cols - 8),
        detail_height=2,
    )
    if choice in (BACK, QUIT):
        return None
    return ("erase", "free", "custom")[choice]


def _guided_options(ui: CursesUI) -> tuple[str, str] | None:
    filesystem = ui.menu(
        "Filesystem",
        "ext4 is the safe default. btrfs adds subvolumes and is a good "
        "choice for advanced users.",
        [
            Row("ext4", note="recommended"),
            Row("btrfs", note="advanced"),
        ],
        footer="Up/Down select   Enter continue   Esc back",
        allow_back=True,
    )
    if filesystem in (BACK, QUIT):
        return None
    swap_size = disk.human_size(layout_module.SWAP_MIB * MIB)
    swap = ui.menu(
        "Swap",
        "A swapfile is easy to resize and needs no partition. A swap "
        "partition is useful for hibernation.",
        [
            Row(
                "Swapfile (recommended)",
                note="{} on the root filesystem".format(swap_size),
            ),
            Row(
                "Swap partition ({})".format(swap_size),
                note="traditional layout",
            ),
            Row("No swap", note="not recommended for a desktop"),
        ],
        footer="Up/Down select   Enter continue   Esc back",
        allow_back=True,
    )
    if swap in (BACK, QUIT):
        return None
    return (
        "ext4" if filesystem == 0 else "btrfs",
        ("swapfile", "partition", "none")[swap],
    )


def _guided_layout_flow(
    ui: CursesUI, probe: Probe, args: argparse.Namespace
) -> tuple[InstallConfig, InstallLayout, list[ProbedDisk], bool] | None:
    while True:
        item = _guided_select_disk(ui, probe)
        if item is None:
            return None
        table = item.table or probe.read_table(item.disk)
        mode = _guided_mode(ui, table)
        if mode is None:
            return None
        if mode == "custom":
            advanced = _advanced_layout_flow(ui, probe, args)
            if advanced is None:
                return None
            return (*advanced, False)
        options = _guided_options(ui)
        if options is None:
            return None
        fstype, swap = options
        layout_swap = "partition" if swap == "partition" else "none"
        try:
            if mode == "erase":
                spec = layout_module.plan_erase_disk(
                    table, fstype=fstype, swap=layout_swap
                )
            else:
                spec = layout_module.plan_free_space(
                    table, fstype=fstype, swap=layout_swap
                )
        except (ValueError, disk.PlanError) as exc:
            ui.message(
                "Cannot plan this install",
                [str(exc)],
                footer="Press any key to retry",
            )
            continue
        spec = replace(
            spec,
            path=item.disk.path,
            serial=item.disk.serial,
            size_bytes=item.disk.size_bytes,
            model=item.disk.model,
        )
        config = InstallConfig(
            layout=InstallSpec(disks=(spec,)),
            confirm_disk=item.disk.path,
            confirm_phrase="ERASE",
            repo=args.repo,
            target=args.target,
            dry_run=args.dry_run,
            swap_mode=swap,
            swap_mib=layout_module.SWAP_MIB,
        )
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
        return config, plan, probed_used, True


def _advanced_layout_flow(
    ui: CursesUI, probe: Probe, args: argparse.Namespace
) -> tuple[InstallConfig, InstallLayout, list[ProbedDisk]] | None:
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
            return None
        selected = _select_disks(ui, probed)
        if selected is None:
            return None
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
            swap_mode=(
                "partition"
                if any(
                    part.role == "swap"
                    for spec in disk_specs
                    for part in spec.partitions
                )
                else "swapfile"
            ),
        )
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
        return config, plan, probed_used


def _account_and_packages(
    ui: CursesUI, config: InstallConfig
) -> bool:
    hostname_value = config.hostname or "tenko"
    timezone_value = config.timezone or "UTC"
    locale_value = config.locale or "C.UTF-8"
    keymap_value = config.keymap or "us"
    admin_value = config.admin_user or "admin"
    while True:
        package_rows = [
            Row("Desktop (tenko-base + xfce-desktop)"),
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
            return False
        config.package_set = "desktop" if package_choice == 0 else "base"
        while True:
            values = ui.form(
                "System options",
                [
                    Field("Hostname", hostname_value),
                    Field("Timezone (IANA name)", timezone_value),
                    Field("Locale", locale_value),
                    Field("Keymap", keymap_value),
                    Field("Admin user", admin_value),
                    Field("Password", "", secret=True),
                    Field("Confirm password", "", secret=True),
                ],
                footer="Tab next   Enter continue   Esc back",
                extra_lines=[
                    "Timezone examples: UTC, Europe/Berlin, America/New_York.",
                    "Locale examples: C.UTF-8, en_US.UTF-8.",
                    "Keymap examples: us, de, uk.",
                    "The admin user is added to the wheel and kvm groups.",
                    "Root stays locked; use sudo from the admin account.",
                ],
            )
            if values is None:
                break
            (
                hostname,
                timezone,
                locale,
                keymap,
                admin,
                password,
                confirm_password,
            ) = values
            hostname_value, admin_value = hostname, admin
            timezone_value, locale_value, keymap_value = timezone, locale, keymap
            if password != confirm_password:
                ui.message(
                    "Passwords do not match",
                    ["Re-enter the admin password."],
                    footer="Press any key to retry",
                )
                continue
            config.hostname = hostname
            config.timezone = timezone
            config.locale = locale
            config.keymap = keymap
            config.admin_user = admin
            config.admin_password = password
            issues = config.validate()
            if issues:
                ui.message(
                    "Invalid options", issues, footer="Press any key to retry"
                )
                continue
            return True


def _confirm_and_install(
    ui: CursesUI,
    config: InstallConfig,
    plan: InstallLayout,
    probe: Probe,
    logger: Logger,
    runner: CommandRunner,
    args: argparse.Namespace,
    *,
    guided: bool,
) -> int | None:
    confirm_lines = _confirm_lines(plan, config)
    destructive = any(item.delete_numbers for item in plan.disks)
    if guided and not destructive:
        key = ui.message(
            "Confirm installation",
            confirm_lines
            + [
                "",
                "Press Enter to install, or q to go back.",
            ],
            footer="Enter install   q cancel",
        )
        if key in (ord("q"), 27):
            return None
    else:
        typed = ui.confirm_typed(
            "Confirm installation",
            confirm_lines,
            ["Type the root disk path", "Type ERASE"],
            footer="Tab next   Enter confirm   Esc back",
        )
        if typed is None:
            return None
        if (
            typed[0].strip() != config.root_disk_path
            or typed[1].strip() != "ERASE"
        ):
            ui.message(
                "Confirmation did not match",
                [
                    "The disk path or ERASE phrase was incorrect.",
                    "Nothing was changed.",
                ],
                footer="Press any key to exit",
            )
            return None
        config.confirm_disk = typed[0].strip()
        config.confirm_phrase = typed[1].strip()

    progress = ui.progress("Installing Tenko Linux", 9)
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
            [
                "Unexpected error: {}".format(exc),
                "Log: " + (logger.human_path or LOG_JSONL),
            ],
            footer="Press any key to exit",
        )
        return 1
    logger.console = None
    progress.finish()

    text = [
        "Tenko Linux 6 (Workstation) {} on {}.".format(
            "simulation finished"
            if getattr(probe, "simulated", False)
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
                    "SIMULATION"
                    if getattr(probe, "simulated", False)
                    else "DRY RUN"
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
    key = ui.message(
        "Installation complete", text, footer="Enter reboot   q exit"
    )
    if args.no_reboot or key in (ord("q"), 27):
        return 0
    try:
        runner.run(
            ("reboot",), step="finish", description="reboot after install"
        )
    except (CommandError, OSError):
        pass
    return 0


def _interactive(
    stdscr,
    args: argparse.Namespace,
    logger: Logger,
    runner: CommandRunner,
    probe: Probe,
) -> int:
    ui = CursesUI(stdscr)
    config = _initial_config(args)
    # A single attempt keeps the first screen responsive; the network setup
    # screen below handles the retry and runs nmtui when needed.
    checks, ok = run_preflight(probe, config, logger, repo_attempts=1)
    while not ok and repository_check_failed(checks):
        if not network_setup_screen(ui, runner, logger):
            return 2
        checks, ok = run_preflight(probe, config, logger, repo_attempts=2)
    lines = [
        "This will install Tenko Linux 6 (Workstation) on a local GPT disk.",
        "",
    ]
    for check in checks:
        lines.append(
            "[{}] {}: {}".format(
                "x" if check.ok else "!", check.label, check.detail
            )
        )
    lines.extend(
        [
            "",
            "The guided install erases one disk and sets up a working "
            "desktop.",
            "The advanced install lets you choose disks, partitions and "
            "mount points,",
            "including /home on a second disk. Existing partitions are "
            "preserved",
            "unless you mark them for deletion. There is no undo after "
            "formatting.",
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
        "Tenko Linux 6 (Workstation) - Installer"
        + (" (simulation)" if getattr(probe, "simulated", False) else ""),
        lines,
        footer="Enter continue   q quit",
    )
    if key in (ord("q"), 27):
        return 0

    while True:
        mode = _install_mode(ui, getattr(probe, "simulated", False))
        if mode is None:
            return 0
        if mode == "guided":
            result = _guided_layout_flow(ui, probe, args)
        else:
            advanced = _advanced_layout_flow(ui, probe, args)
            result = (*advanced, False) if advanced is not None else None
        if result is None:
            continue
        config, plan, probed_used, guided = result
        if not _account_and_packages(ui, config):
            continue
        write_probe_snapshot(probe, probed_used, logger)
        outcome = _confirm_and_install(
            ui,
            config,
            plan,
            probe,
            logger,
            runner,
            args,
            guided=guided,
        )
        if outcome is not None:
            return outcome


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
        print("tenko-installer: {}: {}".format(type(exc).__name__, exc), file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _use_simulated_paths() -> str:
    """Point logs/plans at a writable directory for --simulate."""

    global LOG_DIR, LOG_JSONL, PLAN_JSON
    directory = os.environ.get(
        "TENKO_SIM_DIR", "/tmp/tenko-installer-sim"
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
            "tenko-installer: simulation mode, logs in {}".format(sim_dir),
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
