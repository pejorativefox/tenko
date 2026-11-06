"""Synthetic block devices for interactive dry-run testing.

``tenko-installer --simulate`` swaps the real :class:`probe.Probe` for a
:class:`SimulatedProbe`.  The curses UI, planner, answer-file handling and
install pipeline all run normally, but:

* the disks are in-memory ``lsblk``/``sfdisk`` results;
* the command runner is forced into dry-run mode, so every mutating command
  is written to ``plan.sh`` instead of being executed;
* no root, UEFI firmware, live medium or network is required.

The synthetic disks are intentionally small and predictable so the layout
editor can be exercised quickly during development.
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

import disk
from probe import Check, ProbedDisk

MIB = 1024 * 1024
GIB = 1024 * MIB

SCENARIOS = ("blank", "mixed")


def _total_sectors(size_gib: int, unit: int = 512) -> int:
    return (size_gib * GIB) // unit


def _blank_table(path: str, total: int, unit: int = 512) -> disk.PartitionTable:
    return disk.PartitionTable(
        device=path,
        label="gpt",
        id=str(uuid.uuid4()).upper(),
        unit=unit,
        firstlba=max(1, MIB // unit),
        lastlba=total - 34,
        total_sectors=total,
    )


def _disk(
    path: str,
    size_gib: int,
    model: str,
    serial: str,
    children: tuple[disk.Partition, ...] = (),
    unit: int = 512,
) -> disk.Disk:
    total = _total_sectors(size_gib, unit)
    return disk.Disk(
        path=path,
        kname=os.path.basename(path),
        size_bytes=total * unit,
        sector_size=unit,
        model=model,
        serial=serial,
        tran="sim",
        ro=False,
        pttype="gpt",
        children=children,
        type="disk",
    )


def _blank(path: str, size_gib: int, serial: str) -> ProbedDisk:
    item = _disk(path, size_gib, "Simulated blank disk", serial)
    return ProbedDisk(
        disk=item,
        table=_blank_table(path, item.total_sectors()),
        selectable=True,
    )


def _mixed(path: str, size_gib: int, serial: str) -> ProbedDisk:
    unit = 512
    total = _total_sectors(size_gib, unit)
    table = _blank_table(path, total, unit)
    esp = disk.Partition(
        node=path + "1",
        number=1,
        start=table.firstlba or 2048,
        size=(1024 * MIB) // unit,
        type=disk.ESP_TYPE,
        partuuid="11111111-1111-1111-1111-111111111111",
        name="EFI",
        fs_uuid="1234-ABCD",
        fstype="vfat",
        label="EFI",
    )
    data = disk.Partition(
        node=path + "2",
        number=2,
        start=esp.end,
        size=(8 * GIB) // unit,
        type=disk.LINUX_FS_TYPE,
        partuuid="22222222-2222-2222-2222-222222222222",
        name="Existing data",
        fs_uuid="33333333-4444-5555-6666-777777777777",
        fstype="ext4",
        label="data",
    )
    table = disk.PartitionTable(
        device=path,
        label="gpt",
        id=table.id,
        unit=unit,
        firstlba=table.firstlba,
        lastlba=table.lastlba,
        total_sectors=table.total_sectors,
        partitions=(esp, data),
    )
    item = _disk(
        path,
        size_gib,
        "Simulated disk with existing partitions",
        serial,
        children=(esp, data),
        unit=unit,
    )
    return ProbedDisk(disk=item, table=table, selectable=True)


def synthesize(scenario: str = "blank") -> tuple[ProbedDisk, ...]:
    if scenario not in SCENARIOS:
        raise ValueError(
            "unknown simulation scenario {!r}; choose {}".format(
                scenario, " or ".join(SCENARIOS)
            )
        )
    if scenario == "mixed":
        return (
            _blank("/dev/vda", 20, "SIM-VDA"),
            _mixed("/dev/vdb", 20, "SIM-VDB"),
        )
    return (
        _blank("/dev/vda", 20, "SIM-VDA"),
        _blank("/dev/vdb", 10, "SIM-VDB"),
    )


class SimulatedProbe:
    """Probe-shaped object that never touches a real block device."""

    simulated = True

    def __init__(self, runner, scenario: str = "blank") -> None:
        self.runner = runner
        self.scenario = scenario
        self._disks = synthesize(scenario)

    # -- enumeration / tables ------------------------------------------
    def lsblk(self, refresh: bool = False) -> tuple[disk.Disk, ...]:
        return tuple(item.disk for item in self._disks)

    def probe_disks(self, refresh: bool = False) -> list[ProbedDisk]:
        return list(self._disks)

    def find_disk(self, path: str, refresh: bool = False) -> ProbedDisk | None:
        return next(
            (
                item
                for item in self._disks
                if item.disk.path == path or item.disk.kname == path
            ),
            None,
        )

    def read_table(self, probed: ProbedDisk) -> disk.PartitionTable:
        return probed.table or _blank_table(
            probed.disk.path, probed.disk.total_sectors()
        )

    def detect_live_disk(self, refresh: bool = False) -> str | None:
        return None

    def secure_boot_state(self) -> bool | None:
        return False

    def blkid_uuid(self, device: str) -> str | None:
        for item in self._disks:
            for part in item.disk.children:
                if part.node == device:
                    return part.fs_uuid
        return None

    # -- readiness ----------------------------------------------------
    def wait_for_partuuid(self, plan, timeout: float = 0.0) -> bool:
        return True

    def wait_for_partuuids(self, layout, timeout: float = 0.0) -> bool:
        return True

    def resolve_partition(self, part: disk.PlannedPartition) -> str:
        return part.node or part.by_partuuid

    # -- preflight ----------------------------------------------------
    def preflight(
        self,
        *,
        repo: str,
        target: str,
        live_kname: str | None,
        dry_run: bool = False,
    ) -> list[Check]:
        return [
            Check(
                True,
                "simulated disks",
                "{} synthetic disk(s), scenario {!r}; no real device is "
                "touched".format(len(self._disks), self.scenario),
            )
        ]
