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
import probe as probe_module
from disk import Disk, LayoutPlan, PartitionTable, Region
from install import (
    ConfigError,
    InstallConfig,
    InstallError,
    Installer,
    PACKAGE_SETS,
    TARGET_PACKAGES_DESKTOP,
)
from log import Logger
from probe import Check, Probe, ProbedDisk
from runner import CommandError, CommandRunner
from ui import BACK, QUIT, RESCAN, CursesUI, Field, Row

VERSION = "13.1"
DEFAULT_REPO = "https://tomfool.8bit.ca/browneye/packages/13.1/"
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


def _write_plan_json(plan: LayoutPlan, config: InstallConfig) -> None:
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        payload = {
            "version": 1,
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


def write_probe_snapshot(probe: Probe, probed: ProbedDisk, logger: Logger) -> None:
    """Write /run/browneye/probe.json for post-mortem debugging."""

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
        "secure_boot": probe.secure_boot_state(),
        "disk": {
            "path": probed.disk.path,
            "kname": probed.disk.kname,
            "model": probed.disk.model,
            "serial": probed.disk.serial,
            "size_bytes": probed.disk.size_bytes,
            "sector_size": probed.disk.sector_size,
            "pttype": probed.disk.pttype,
            "live": probed.live,
            "selectable": probed.selectable,
            "reasons": list(probed.reasons),
            "table": asdict(probed.table) if probed.table is not None else None,
        },
    }
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


def _disk_matches(probed: ProbedDisk, config: InstallConfig) -> list[str]:
    issues: list[str] = []
    if config.disk_serial:
        if not probed.disk.serial:
            issues.append("the answer file requires a serial but the disk has none")
        elif config.disk_serial.casefold() != probed.disk.serial.casefold():
            issues.append(
                "disk serial changed: {} != {}".format(
                    probed.disk.serial, config.disk_serial
                )
            )
    if config.disk_size_bytes is not None and probed.disk.size_bytes != config.disk_size_bytes:
        issues.append(
            "disk size changed: {} != {}".format(
                probed.disk.size_bytes, config.disk_size_bytes
            )
        )
    if not config.disk_serial and config.disk_model and probed.disk.model:
        if config.disk_model.strip().casefold() != probed.disk.model.strip().casefold():
            issues.append(
                "disk model changed: {} != {}".format(
                    probed.disk.model, config.disk_model
                )
            )
    return issues


def build_plan(
    probe: Probe,
    config: InstallConfig,
) -> tuple[LayoutPlan, ProbedDisk, list[Region]]:
    probed = probe.find_disk(config.disk_path, refresh=True)
    if probed is None:
        raise ConfigError(f"disk {config.disk_path} was not found")
    if probed.live:
        raise ConfigError("the selected disk is the live installation media")
    if not probed.selectable:
        raise ConfigError(
            "disk {} is not selectable: {}".format(
                config.disk_path, "; ".join(probed.reasons) or "unknown reason"
            )
        )
    issues = _disk_matches(probed, config)
    if issues:
        raise ConfigError("; ".join(issues))
    table = probed.table or probe.read_table(probed.disk)
    remaining = table.without(config.delete_partitions)
    regions = disk.find_free_regions(
        remaining,
        total_sectors=table.total_sectors,
        unit=table.unit,
        align=max(1, MIB // (table.unit or 512)),
    )
    if not regions:
        raise ConfigError(
            "disk {} has no free region of at least 2 MiB".format(config.disk_path)
        )
    region = disk.choose_region(
        regions,
        required_mib=0,
        start_mib=config.region_start_mib,
    )
    if region is None:
        raise ConfigError(
            "the requested free region was not found on {}".format(config.disk_path)
        )
    plan = disk.plan_layout(
        table,
        region,
        disk_path=config.disk_path,
        esp_mib=config.esp_mib,
        root_mib=config.root_mib,
        swap_mib=config.swap_mib,
        root_min_mib=8192,
        delete_numbers=config.delete_partitions,
        total_sectors=table.total_sectors,
        unit=table.unit,
    )
    issues = disk.validate_plan(plan)
    if issues:
        raise ConfigError("invalid layout: " + "; ".join(issues))
    return plan, probed, regions


# ---------------------------------------------------------------------------
# Shared install runner
# ---------------------------------------------------------------------------


def execute_install(
    config: InstallConfig,
    plan: LayoutPlan,
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
        plan, probed, _regions = build_plan(probe, config)
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


def run_plain(
    args: argparse.Namespace,
    logger: Logger,
    runner: CommandRunner,
    probe: Probe,
) -> int:
    answer_path = find_answer_path(args.answer)
    if answer_path:
        return run_noninteractive(args, logger, runner, probe)

    console = lambda line: console_line(line)
    logger.console = console
    config = InstallConfig(
        disk_path="",
        repo=args.repo,
        target=args.target,
        dry_run=args.dry_run,
    )
    checks, ok = run_preflight(probe, config, logger)
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
    print("Select a disk:")
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
    choice = _ask("Disk number", "1")
    try:
        selected = selectable[int(choice) - 1]
    except (ValueError, IndexError):
        marker("FAIL disk selection")
        return 2
    table = selected.table or probe.read_table(selected.disk)
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
    delete_text = _ask("Delete partition numbers (comma-separated, blank = none)", "")
    deleted: list[int] = []
    for token in delete_text.replace(" ", "").split(","):
        if not token:
            continue
        try:
            deleted.append(int(token))
        except ValueError:
            marker("FAIL delete list")
            return 2
    remaining = table.without(deleted)
    regions = disk.find_free_regions(
        remaining,
        total_sectors=table.total_sectors,
        unit=table.unit,
        align=max(1, MIB // (table.unit or 512)),
    )
    if not regions:
        print("No usable free region.")
        return 2
    print("\nFree regions:")
    usable = [region for region in regions if region.size_mib >= 8192]
    for index, region in enumerate(regions, 1):
        note = "" if region in usable else "  (too small for an 8 GiB root)"
        print(
            "  {}. {}..{} MiB  {} MiB{}".format(
                index, region.start_mib, region.end_mib, region.size_mib, note
            )
        )
    choice = _ask("Region number", str(regions.index(max(regions, key=lambda r: r.size_mib)) + 1))
    try:
        region = regions[int(choice) - 1]
    except (ValueError, IndexError):
        marker("FAIL region selection")
        return 2
    root_text = _ask("Root size MiB (blank = fill region)", "")
    swap_text = _ask("Swap size MiB (0 = none)", "2048")
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
    try:
        config = InstallConfig(
            disk_path=selected.disk.path,
            disk_serial=selected.disk.serial,
            disk_size_bytes=selected.disk.size_bytes,
            disk_model=selected.disk.model,
            delete_partitions=tuple(deleted),
            region_start_mib=region.start_mib,
            root_mib=int(root_text) if root_text else None,
            swap_mib=int(swap_text) if swap_text else 0,
            package_set=package_set if package_set in PACKAGE_SETS else "desktop",
            hostname=hostname,
            admin_user=admin,
            admin_password=password,
            confirm_disk=selected.disk.path,
            confirm_phrase="ERASE",
            repo=args.repo,
            target=args.target,
            dry_run=args.dry_run,
        )
    except ValueError:
        marker("FAIL size: root and swap sizes must be integers")
        return 2
    issues = config.validate()
    if issues:
        print("Configuration errors: " + "; ".join(issues))
        return 2
    try:
        plan, probed, _regions = build_plan(probe, config)
    except (ConfigError, disk.PlanError) as exc:
        marker("FAIL plan: " + str(exc))
        return 2
    write_probe_snapshot(probe, probed, logger)
    print("\nPlan:")
    print("  disk:   {}".format(plan.disk_path))
    print("  region: {}..{} MiB".format(plan.region.start_mib, plan.region.end_mib))
    print("  delete: {}".format(", ".join(map(str, plan.delete_numbers)) or "none"))
    print("  esp:    {} ({} MiB){}".format(
        plan.esp.by_partuuid,
        (plan.esp.size * plan.unit) // MIB,
        " reuse" if plan.esp.existing else "",
    ))
    if plan.swap:
        print("  swap:   {} MiB".format((plan.swap.size * plan.unit) // MIB))
    print("  root:   {} MiB ext4".format((plan.root.size * plan.unit) // MIB))
    for warning in plan.warnings:
        print("  warning: " + warning)
    print("\nThere is no undo after formatting begins.")
    typed_disk = _ask("Type the disk path to confirm", "")
    typed_phrase = _ask("Type ERASE to start", "")
    if typed_disk != plan.disk_path or typed_phrase != "ERASE":
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


def _partition_rows(table: PartitionTable, deleted: set[int]) -> list[Row]:
    rows: list[Row] = []
    for part in sorted(table.partitions, key=lambda p: p.number):
        marker = "[x]" if part.number in deleted else "[ ]"
        detail = "{}  start {} MiB  size {} MiB  {}".format(
            part.number,
            (part.start * table.unit) // MIB,
            (part.size * table.unit) // MIB,
            disk.type_name(part.type, table.is_mbr),
        )
        if part.name:
            detail += "  " + part.name
        elif part.partuuid:
            detail += "  " + part.partuuid
        rows.append(Row(detail, marker=marker))
    return rows


def _region_rows(regions: Sequence[Region], minimum_mib: int = 8192) -> list[Row]:
    rows = []
    for region in regions:
        enabled = region.size_mib >= minimum_mib
        text = "{}..{} MiB   {} MiB".format(
            region.start_mib, region.end_mib, region.size_mib
        )
        note = "" if enabled else "too small for an 8 GiB root"
        rows.append(Row(text, enabled=enabled, note=note))
    return rows


def _initial_config(args: argparse.Namespace) -> InstallConfig:
    return InstallConfig(
        disk_path="",
        repo=args.repo,
        target=args.target,
        dry_run=args.dry_run,
    )


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
        "This will install Browneye Linux 13.1 on a local GPT disk.",
        "",
    ]
    for check in checks:
        lines.append(
            "[{}] {}: {}".format("x" if check.ok else "!", check.label, check.detail)
        )
    lines.extend(
        [
            "",
            "UEFI only. Existing partitions are preserved; only the selected",
            "disk is modified. There is no undo after formatting begins.",
        ]
    )
    if not ok:
        ui.message("Preflight failed", lines, footer="Press any key to exit")
        return 2
    key = ui.message(
        "Browneye Linux 13.1 - Installer",
        lines,
        footer="Enter continue   q quit",
    )
    if key in (ord("q"), 27):
        return 0

    while True:
        probed = probe.probe_disks(refresh=True)
        rows = []
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
                    note="",
                )
            )
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
        choice = ui.menu(
            "Select installation disk",
            "Only disks with no mounted partitions or holders are selectable.",
            rows,
            footer="Up/Down select   Enter continue   r rescan   q quit",
        )
        if choice == QUIT:
            return 0
        if choice == RESCAN:
            continue
        selected = probed[choice]
        if not selected.selectable:
            continue
        break

    table = selected.table or probe.read_table(selected.disk)
    deleted: set[int] = set()
    while True:
        parts = table.partitions
        rows = _partition_rows(table, deleted)
        rows.append(Row("Continue with these deletions"))
        action = ui.menu(
            "Partition editor - {}".format(selected.disk.path),
            "{}  {}  {}".format(
                disk.human_size(selected.disk.size_bytes),
                table.label.upper() if table.label else "blank",
                selected.disk.model or "",
            ),
            rows,
            footer="Up/Down select   Enter toggle/continue   r rescan   Esc back",
            allow_back=True,
        )
        if action == BACK:
            # Re-run the disk selection from the top.
            return _interactive(stdscr, args, logger, runner, probe)
        if action == RESCAN:
            selected = probe.find_disk(selected.disk.path, refresh=True) or selected
            table = selected.table or probe.read_table(selected.disk)
            continue
        if action == QUIT:
            return 0
        if action == len(rows) - 1:
            break
        number = parts[action].number
        if number in deleted:
            deleted.remove(number)
        else:
            deleted.add(number)

    remaining = table.without(deleted)
    regions = disk.find_free_regions(
        remaining,
        total_sectors=table.total_sectors,
        unit=table.unit,
        align=max(1, MIB // (table.unit or 512)),
    )
    if not regions:
        ui.message(
            "No free space",
            [
                "The disk has no contiguous free region of at least 2 MiB.",
                "Delete a partition or choose another disk.",
            ],
            footer="Press any key to go back",
        )
        return _interactive(stdscr, args, logger, runner, probe)
    has_esp = any(
        (part.type or "").upper() == disk.ESP_TYPE
        for part in remaining.partitions
    )
    required_mib = 8192 if has_esp else 9216
    region_rows = _region_rows(regions, required_mib)
    if not any(row.enabled for row in region_rows):
        ui.message(
            "Free space is too small",
            [
                "The largest free region is {} MiB; at least {} MiB is required ".format(
                    max(region.size_mib for region in regions), required_mib
                )
                + ("for the root filesystem." if has_esp else "for a 1 GiB ESP and an 8 GiB root."),
                "Delete more partitions or choose another disk.",
            ],
            footer="Press any key to go back",
        )
        return _interactive(stdscr, args, logger, runner, probe)
    region_choice = ui.menu(
        "Select free region",
        "The installer only writes inside the chosen region.",
        region_rows,
        footer="Up/Down select   Enter continue   Esc back",
        allow_back=True,
    )
    if region_choice in (BACK, QUIT):
        return _interactive(stdscr, args, logger, runner, probe)
    region = regions[region_choice]

    # Sizing loop -------------------------------------------------------
    plan: LayoutPlan | None = None
    while True:
        try:
            candidate = disk.plan_layout(
                table,
                region,
                disk_path=selected.disk.path,
                esp_mib=disk.ESP_MIB,
                root_mib=None,
                swap_mib=2048,
                root_min_mib=8192,
                delete_numbers=tuple(sorted(deleted)),
                total_sectors=table.total_sectors,
                unit=table.unit,
            )
        except disk.PlanError as exc:
            ui.message("Cannot plan layout", [str(exc)], footer="Press any key to go back")
            return _interactive(stdscr, args, logger, runner, probe)
        esp_mib = (candidate.esp.size * candidate.unit) // MIB
        max_root = (candidate.root.size * candidate.unit) // MIB
        swap_mib = (
            (candidate.swap.size * candidate.unit) // MIB if candidate.swap else 0
        )
        extra = [
            "Region: {}..{} MiB".format(region.start_mib, region.end_mib),
            "ESP: {}".format(
                "reuse existing {} MiB partition".format(esp_mib)
                if candidate.esp.existing
                else "create {} MiB".format(esp_mib)
            ),
            "Swap: {} MiB{}".format(
                swap_mib,
                "" if swap_mib else " (skipped; region too small)",
            ),
            "Maximum root size: {} MiB".format(max_root),
        ]
        values = ui.form(
            "Install layout",
            [
                Field("Root size (MiB, blank = fill)", ""),
                Field("Swap size (MiB, 0 = none)", str(swap_mib or 0)),
            ],
            footer="Tab next   Enter continue   Esc back",
            extra_lines=extra,
        )
        if values is None:
            return _interactive(stdscr, args, logger, runner, probe)
        root_text, swap_text = values
        try:
            root_mib = int(root_text) if root_text.strip() else None
            chosen_swap = int(swap_text) if swap_text.strip() else 0
            plan = disk.plan_layout(
                table,
                region,
                disk_path=selected.disk.path,
                esp_mib=disk.ESP_MIB,
                root_mib=root_mib,
                swap_mib=chosen_swap,
                root_min_mib=8192,
                delete_numbers=tuple(sorted(deleted)),
                total_sectors=table.total_sectors,
                unit=table.unit,
            )
        except (ValueError, disk.PlanError) as exc:
            ui.message("Invalid size", [str(exc)], footer="Press any key to retry")
            continue
        issues = disk.validate_plan(plan)
        if issues:
            ui.message("Invalid layout", issues, footer="Press any key to retry")
            continue
        break

    # Account and package set ------------------------------------------
    while True:
        package_rows = [
            Row("Desktop (browneye-base + xfce-desktop)"),
            Row("Base only (no desktop)"),
        ]
        package_choice = ui.menu(
            "Package set",
            "The target always includes the kernel, modules, systemd-boot, "
            "dracut, "
            "efibootmgr, dosfstools and dnf.",
            package_rows,
            footer="Up/Down select   Enter continue   Esc back",
            allow_back=True,
        )
        if package_choice in (BACK, QUIT):
            return _interactive(stdscr, args, logger, runner, probe)
        package_set = "desktop" if package_choice == 0 else "base"
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
            return _interactive(stdscr, args, logger, runner, probe)
        hostname, admin, password, confirm_password = values
        if password != confirm_password:
            ui.message(
                "Passwords do not match",
                ["Re-enter the admin password."],
                footer="Press any key to retry",
            )
            continue
        config = InstallConfig(
            disk_path=selected.disk.path,
            disk_serial=selected.disk.serial,
            disk_size_bytes=selected.disk.size_bytes,
            disk_model=selected.disk.model,
            delete_partitions=tuple(sorted(deleted)),
            region_start_mib=region.start_mib,
            esp_mib=disk.ESP_MIB,
            root_mib=(plan.root.size * plan.unit) // MIB,
            swap_mib=((plan.swap.size * plan.unit) // MIB if plan.swap else 0),
            package_set=package_set,
            hostname=hostname,
            admin_user=admin,
            admin_password=password,
            confirm_disk=selected.disk.path,
            confirm_phrase="ERASE",
            repo=args.repo,
            target=args.target,
            dry_run=args.dry_run,
        )
        issues = config.validate()
        if issues:
            ui.message("Invalid options", issues, footer="Press any key to retry")
            continue
        # Keep the exact plan the user saw; re-plan with the same sizes.
        try:
            plan, probed, _regions = build_plan(probe, config)
        except (ConfigError, disk.PlanError) as exc:
            ui.message("Cannot plan", [str(exc)], footer="Press any key to retry")
            continue
        write_probe_snapshot(probe, probed, logger)
        break

    # Confirm ----------------------------------------------------------
    confirm_lines = [
        "Disk:    {}  {}".format(
            plan.disk_path,
            disk.human_size(plan.disk_size_bytes),
        ),
        "Delete:  {}".format(
            ", ".join("partition {}".format(n) for n in plan.delete_numbers) or "none"
        ),
        "Region:  {}..{} MiB".format(plan.region.start_mib, plan.region.end_mib),
        "ESP:     {} MiB {}".format(
            (plan.esp.size * plan.unit) // MIB,
            "(reuse)" if plan.esp.existing else "(new)",
        ),
        "Swap:    {}".format(
            "{} MiB".format((plan.swap.size * plan.unit) // MIB)
            if plan.swap
            else "none (skipped)"
        ),
        "Root:    {} MiB ext4".format((plan.root.size * plan.unit) // MIB),
        "Install: {}".format(", ".join(config.packages)),
        "",
        "This ERASES the selected partitions. Other partitions are preserved.",
        "There is no undo after formatting begins.",
    ]
    for warning in plan.warnings:
        confirm_lines.append("Warning: " + warning)
    typed = ui.confirm_typed(
        "Confirm installation",
        confirm_lines,
        ["Type the disk path", "Type ERASE"],
        footer="Tab next   Enter confirm   Esc back",
    )
    if typed is None:
        return _interactive(stdscr, args, logger, runner, probe)
    if typed[0].strip() != plan.disk_path or typed[1].strip() != "ERASE":
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
        "Browneye Linux 13.1 was installed on {}.".format(plan.disk_path),
        "",
        "Log: {}".format(logger.human_path or LOG_JSONL),
    ]
    if config.dry_run:
        text.extend(
            [
                "",
                "DRY RUN: no disk was modified.",
                "The exact mutating commands are in /run/browneye/plan.sh.",
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


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    logger = Logger(
        LOG_JSONL,
        console=console_line if (args.non_interactive or args.plain) else None,
    )
    logger.session_header(
        version=VERSION,
        dry_run=args.dry_run,
        non_interactive=args.non_interactive,
        plain=args.plain,
    )
    runner = CommandRunner(logger, dry_run=args.dry_run)
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
