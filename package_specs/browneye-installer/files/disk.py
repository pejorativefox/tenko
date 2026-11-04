"""Pure disk planning for the Browneye installer.

Nothing in this module executes a command.  It parses ``sfdisk --json`` and
``lsblk --json``, computes free regions (including the GPT tail gap before the
backup table), plans the ESP/swap/root layout, renders a complete replacement
partition table, verifies that untouched entries were preserved, and emits
:class:`runner.Command` objects for the install pipeline to execute.

The only inputs are JSON text, sector counts and small integers, so the
planner runs in unit tests without root and without touching a disk.

Sector units
------------
All ``start``/``size`` values are in the disk's logical sectors as reported by
``sfdisk --json`` (``sectorsize``: 512 on 512e/512n, 4096 on 4Kn).  Never
assume 512.  ``blockdev --getsz`` reports 512-byte sectors, so the probe
converts: ``table_total = getsz * 512 // sectorsize``.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass, field, replace
from typing import Any, Callable, Iterable, Sequence

from runner import Command

MIB = 1024 * 1024
GIB = 1024 * MIB

ESP_TYPE = "C12A7328-F81F-11D2-BA4B-00A0C93EC93B"
LINUX_FS_TYPE = "0FC63DAF-8483-4772-8E79-3D69D8477DE4"
LINUX_SWAP_TYPE = "0657FD6D-A4AB-43C4-84E5-0933C84B4F4F"

# Common GPT type names shown in the UI.  Unknown GUIDs are shown as-is.
GPT_TYPE_NAMES = {
    ESP_TYPE: "EFI System",
    "EBD0A0A2-B9E5-4433-87C0-68B6B72699C7": "Microsoft basic data",
    "E3C9E316-0B5C-4DB8-817D-F92DF00215AE": "Microsoft reserved",
    "DE94BBA4-06D1-4D40-A16A-BFD50179D6AC": "Windows recovery",
    LINUX_FS_TYPE: "Linux filesystem",
    LINUX_SWAP_TYPE: "Linux swap",
    "E6D6D379-F507-44C2-A23C-238F2A3DF928": "Linux LVM",
    "CA7D7CCB-63ED-4C53-861C-1742536059CC": "Linux LUKS",
    "21686148-6449-6E6F-744E-656564454649": "BIOS boot",
}

MBR_TYPE_NAMES = {
    "83": "Linux filesystem",
    "82": "Linux swap",
    "ef": "EFI System",
    "05": "Extended",
    "0f": "Extended (LBA)",
    "85": "Extended (Linux)",
    "07": "NTFS/exFAT",
    "0b": "FAT32",
    "0c": "FAT32 (LBA)",
}

MBR_EXTENDED = {"5", "05", "f", "0f", "85"}
DEFAULT_ALIGN_MIB = 1
MIN_REGION_MIB = 2
ROOT_MIN_MIB = 8192
SWAP_MIB = 2048
ESP_MIB = 1024


class PlanError(RuntimeError):
    """The requested layout cannot be planned safely."""


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Partition:
    """A partition entry.

    ``partuuid`` is the GPT partition GUID (``sfdisk``'s ``uuid`` and lsblk's
    ``PARTUUID``).  ``fs_uuid`` is the filesystem UUID (lsblk ``UUID``).
    """

    node: str = ""
    number: int = 0
    start: int = 0
    size: int = 0
    type: str = ""
    partuuid: str | None = None
    name: str | None = None
    attrs: str | None = None
    fs_uuid: str | None = None
    fstype: str | None = None
    label: str | None = None
    mountpoint: str | None = None

    @property
    def end(self) -> int:
        return self.start + self.size


@dataclass(frozen=True)
class PartitionTable:
    device: str = ""
    label: str | None = None
    id: str | None = None
    unit: int = 512
    firstlba: int | None = None
    lastlba: int | None = None
    total_sectors: int | None = None
    partitions: tuple[Partition, ...] = ()

    @property
    def is_gpt(self) -> bool:
        return (self.label or "").lower() == "gpt"

    @property
    def is_mbr(self) -> bool:
        return (self.label or "").lower() in ("dos", "mbr")

    @property
    def is_blank(self) -> bool:
        return not self.label and not self.partitions

    def by_number(self) -> dict[int, Partition]:
        return {part.number: part for part in self.partitions}

    def without(self, numbers: Iterable[int]) -> "PartitionTable":
        drop = set(numbers)
        return replace(
            self,
            partitions=tuple(p for p in self.partitions if p.number not in drop),
        )

    def find_number(self, number: int) -> Partition | None:
        for part in self.partitions:
            if part.number == number:
                return part
        return None

    def has_extended(self) -> bool:
        if not self.is_mbr:
            return False
        return any((p.type or "").lower().lstrip("0x") in MBR_EXTENDED for p in self.partitions)


@dataclass(frozen=True)
class Disk:
    """A whole-disk view from lsblk (used by probe/UI, not by the planner)."""

    path: str
    kname: str
    size_bytes: int = 0
    sector_size: int = 512
    model: str | None = None
    serial: str | None = None
    tran: str | None = None
    ro: bool = False
    pttype: str | None = None
    children: tuple[Partition, ...] = ()
    mountpoints: tuple[str, ...] = ()
    holders: tuple[str, ...] = ()
    is_live: bool = False
    fstype: str | None = None
    label: str | None = None
    type: str = "disk"

    @property
    def size_gib(self) -> float:
        return self.size_bytes / GIB

    def total_sectors(self, unit: int | None = None) -> int:
        unit = unit or self.sector_size or 512
        return self.size_bytes // unit


@dataclass(frozen=True)
class Region:
    """A contiguous free region.

    ``start`` is inclusive and ``end`` is exclusive.  Both are in table
    sectors (see the module docstring).
    """

    start: int
    end: int
    unit: int = 512
    usable: bool = True
    reason: str = ""

    @property
    def size(self) -> int:
        return self.end - self.start

    @property
    def start_mib(self) -> int:
        return (self.start * self.unit) // MIB

    @property
    def end_mib(self) -> int:
        return (self.end * self.unit) // MIB

    @property
    def size_mib(self) -> int:
        return (self.size * self.unit) // MIB

    def contains(self, start: int, size: int) -> bool:
        return start >= self.start and start + size <= self.end


@dataclass(frozen=True)
class PlannedPartition:
    role: str
    number: int
    start: int
    size: int
    type: str
    partuuid: str
    fs_uuid: str | None
    name: str
    existing: bool = False
    node: str = ""

    @property
    def end(self) -> int:
        return self.start + self.size

    @property
    def by_partuuid(self) -> str:
        # udev creates the by-partuuid symlinks with lower-case UUIDs, while
        # sfdisk reports GPT GUIDs in upper case.
        return "/dev/disk/by-partuuid/" + self.partuuid.lower()

    @property
    def fat_volume_id(self) -> str | None:
        if self.role != "esp" or not self.fs_uuid:
            return None
        return self.fs_uuid.replace("-", "")[:8].upper()


@dataclass(frozen=True)
class LayoutPlan:
    disk_path: str
    disk_id: str
    table: PartitionTable
    region: Region
    esp: PlannedPartition
    swap: PlannedPartition | None
    root: PlannedPartition
    new_table_text: str
    warnings: tuple[str, ...] = ()
    delete_numbers: tuple[int, ...] = ()
    unit: int = 512
    total_sectors: int | None = None
    first_lba: int = 2048
    last_lba: int = 0
    root_min_mib: int = ROOT_MIN_MIB
    esp_mib: int = ESP_MIB

    @property
    def new_partitions(self) -> tuple[PlannedPartition, ...]:
        parts = []
        if not self.esp.existing:
            parts.append(self.esp)
        if self.swap is not None:
            parts.append(self.swap)
        parts.append(self.root)
        return tuple(sorted(parts, key=lambda p: p.number))

    @property
    def allowed_new_numbers(self) -> tuple[int, ...]:
        return tuple(p.number for p in self.new_partitions)

    @property
    def align(self) -> int:
        return max(1, MIB // self.unit)

    @property
    def disk_size_bytes(self) -> int:
        total = self.total_sectors or self.table.total_sectors
        return (total * self.unit) if total else 0

    def part_for_number(self, number: int) -> PlannedPartition | None:
        if self.esp.number == number:
            return self.esp
        if self.swap is not None and self.swap.number == number:
            return self.swap
        if self.root.number == number:
            return self.root
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "disk": self.disk_path,
            "disk_id": self.disk_id,
            "disk_size_bytes": self.disk_size_bytes,
            "unit": self.unit,
            "first_lba": self.first_lba,
            "last_lba": self.last_lba,
            "region": {
                "start": self.region.start,
                "end": self.region.end,
                "size": self.region.size,
                "start_mib": self.region.start_mib,
                "end_mib": self.region.end_mib,
                "size_mib": self.region.size_mib,
            },
            "delete_partitions": list(self.delete_numbers),
            "esp": _planned_dict(self.esp),
            "swap": _planned_dict(self.swap) if self.swap else None,
            "root": _planned_dict(self.root),
            "warnings": list(self.warnings),
            "table": self.new_table_text,
        }


def _planned_dict(part: PlannedPartition | None) -> dict[str, Any] | None:
    if part is None:
        return None
    return {
        "role": part.role,
        "number": part.number,
        "start": part.start,
        "size": part.size,
        "type": part.type,
        "partuuid": part.partuuid,
        "fs_uuid": part.fs_uuid,
        "name": part.name,
        "existing": part.existing,
    }


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if item not in (None, "")]
    return []


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _number_from_node(node: str | None) -> int:
    if not node:
        return 0
    match = re.search(r"(\d+)$", str(node))
    return int(match.group(1)) if match else 0


def parse_sfdisk_json(
    raw: str | dict[str, Any] | None,
    *,
    device: str | None = None,
    total_sectors: int | None = None,
    unit: int | None = None,
) -> PartitionTable:
    """Parse ``sfdisk --json`` output.

    A blank disk makes sfdisk exit non-zero with no JSON object; callers pass
    the empty string and get an empty table.  ``total_sectors`` must be in
    table sectors when known (the probe converts it from ``blockdev --getsz``).
    """

    if raw in (None, ""):
        return PartitionTable(
            device=device or "",
            unit=unit or 512,
            total_sectors=total_sectors,
        )
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            return PartitionTable(
                device=device or "",
                unit=unit or 512,
                total_sectors=total_sectors,
            )
    elif isinstance(raw, dict):
        data = raw
    else:
        raise TypeError("raw must be JSON text or a dict")

    table = data.get("partitiontable") if isinstance(data, dict) else None
    if not isinstance(table, dict):
        return PartitionTable(
            device=device or "",
            unit=unit or 512,
            total_sectors=total_sectors,
        )

    table_unit = unit or _int(table.get("sectorsize") or table.get("sector-size"), 512)
    if table_unit <= 0:
        table_unit = 512
    firstlba = table.get("firstlba")
    lastlba = table.get("lastlba")
    parts: list[Partition] = []
    for item in table.get("partitions") or []:
        if not isinstance(item, dict):
            continue
        node = _clean(item.get("node")) or ""
        number = _int(item.get("number")) or _number_from_node(node)
        start = _int(item.get("start"))
        size = _int(item.get("size"))
        ptype = _clean(item.get("type")) or ""
        partuuid = _clean(item.get("uuid")) or _clean(item.get("partuuid"))
        name = _clean(item.get("name"))
        attrs = _clean(item.get("attrs"))
        parts.append(
            Partition(
                node=node or (f"{device}{number}" if device and number else ""),
                number=number,
                start=start,
                size=size,
                type=ptype,
                partuuid=partuuid,
                name=name,
                attrs=attrs,
                fs_uuid=_clean(item.get("fs_uuid")),
                fstype=_clean(item.get("fstype")),
                label=_clean(item.get("label")),
            )
        )
    parts.sort(key=lambda p: (p.start, p.number))
    return PartitionTable(
        device=_clean(table.get("device")) or device or "",
        label=_clean(table.get("label")),
        id=_clean(table.get("id")),
        unit=table_unit,
        firstlba=_int(firstlba) if firstlba not in (None, "") else None,
        lastlba=_int(lastlba) if lastlba not in (None, "") else None,
        total_sectors=total_sectors,
        partitions=tuple(parts),
    )


def _parse_lsblk_partition(node: dict[str, Any], parent: dict[str, Any]) -> Partition:
    name = _clean(node.get("name")) or _clean(node.get("kname")) or ""
    node_path = _clean(node.get("path")) or ("/dev/" + name if name else "")
    number = _int(node.get("partn")) or _number_from_node(name)
    sector_size = _int(
        node.get("log-sec") or node.get("log_sec") or parent.get("log-sec"), 512
    ) or 512
    size_bytes = _int(node.get("size"))
    return Partition(
        node=node_path,
        number=number,
        start=0,
        size=size_bytes // sector_size if size_bytes else 0,
        type=_clean(node.get("type")) or "",
        partuuid=_clean(node.get("partuuid")),
        name=_clean(node.get("label")) or _clean(node.get("partlabel")),
        fs_uuid=_clean(node.get("uuid")),
        fstype=_clean(node.get("fstype")),
        label=_clean(node.get("label")),
        mountpoint=(
            _as_list(node.get("mountpoints"))[0]
            if _as_list(node.get("mountpoints"))
            else _clean(node.get("mountpoint"))
        ),
    )


def _parse_lsblk_disk(node: dict[str, Any]) -> Disk:
    name = _clean(node.get("name")) or _clean(node.get("kname")) or ""
    kname = _clean(node.get("kname")) or name
    path = _clean(node.get("path")) or ("/dev/" + name if name else "")
    sector_size = _int(node.get("log-sec") or node.get("log_sec"), 512) or 512
    children = tuple(
        _parse_lsblk_partition(child, node)
        for child in (node.get("children") or [])
        if isinstance(child, dict)
    )
    mountpoints: list[str] = []
    for item in _as_list(node.get("mountpoints")):
        mountpoints.append(item)
    if node.get("mountpoint"):
        mountpoints.append(str(node["mountpoint"]))
    for child in children:
        if child.mountpoint:
            mountpoints.append(child.mountpoint)
    return Disk(
        path=path,
        kname=kname,
        size_bytes=_int(node.get("size")),
        sector_size=sector_size,
        model=_clean(node.get("model")),
        serial=_clean(node.get("serial")),
        tran=_clean(node.get("tran")),
        ro=bool(node.get("ro")),
        pttype=_clean(node.get("pttype")),
        children=children,
        mountpoints=tuple(dict.fromkeys(mountpoints)),
        fstype=_clean(node.get("fstype")),
        label=_clean(node.get("label")),
        type=_clean(node.get("type")) or "disk",
    )


def parse_lsblk_json(raw: str | dict[str, Any]) -> tuple[Disk, ...]:
    """Parse ``lsblk --json`` output into whole disks with their children."""

    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            return ()
    elif isinstance(raw, dict):
        data = raw
    else:
        raise TypeError("raw must be JSON text or a dict")
    devices = data.get("blockdevices") if isinstance(data, dict) else None
    if not isinstance(devices, list):
        return ()
    disks = []
    for node in devices:
        if not isinstance(node, dict):
            continue
        if (_clean(node.get("type")) or "") != "disk":
            continue
        disks.append(_parse_lsblk_disk(node))
    return tuple(disks)


# ---------------------------------------------------------------------------
# Free-space geometry
# ---------------------------------------------------------------------------


def align_up(value: int, alignment: int) -> int:
    if alignment <= 1:
        return value
    return ((value + alignment - 1) // alignment) * alignment


def align_down(value: int, alignment: int) -> int:
    if alignment <= 1:
        return value
    return (value // alignment) * alignment


def _usable_bounds(
    table: PartitionTable,
    total_sectors: int | None,
    unit: int,
    align: int,
) -> tuple[int, int]:
    total = total_sectors if total_sectors is not None else table.total_sectors
    if table.is_mbr:
        if total is None:
            raise PlanError("MBR total sector count is required")
        return align, total
    if table.is_gpt:
        low = table.firstlba if table.firstlba is not None else align
        if table.lastlba is not None:
            high = table.lastlba + 1
        elif total is not None:
            # GPT reserves 33 sectors at the end: LBA total-33..total-1.
            high = total - 33
        else:
            raise PlanError("GPT last usable LBA or total sector count is required")
        return int(low), int(high)
    # Blank/unrecognised table: assume a fresh GPT.
    low = table.firstlba if table.firstlba is not None else align
    if table.lastlba is not None:
        high = table.lastlba + 1
    elif total is not None:
        high = total - 33
    else:
        raise PlanError("total sector count is required for a blank disk")
    return int(low), int(high)


def find_free_regions(
    table: PartitionTable,
    total_sectors: int | None = None,
    unit: int | None = None,
    align: int | None = None,
    min_mib: int = MIN_REGION_MIB,
) -> list[Region]:
    """Return aligned contiguous free regions, largest-first is left to caller.

    The GPT tail gap ends at ``lastlba`` (inclusive), never at the device end,
    so the backup GPT is never included.
    """

    sector_unit = unit or table.unit or 512
    if sector_unit <= 0:
        sector_unit = 512
    alignment = align or max(1, MIB // sector_unit)
    low, high = _usable_bounds(table, total_sectors, sector_unit, alignment)
    low = max(0, low)
    high = max(0, high)
    if high <= low:
        return []

    regions: list[Region] = []

    def add(start: int, end: int) -> None:
        start = align_up(max(start, low), alignment)
        end = align_down(min(end, high), alignment)
        if end <= start:
            return
        size = end - start
        if size * sector_unit < min_mib * MIB:
            return
        regions.append(Region(start=start, end=end, unit=sector_unit))

    cursor = low
    for part in sorted(table.partitions, key=lambda p: (p.start, p.number)):
        pstart = max(part.start, low)
        pend = max(part.end, pstart)
        if pstart > cursor:
            add(cursor, pstart)
        cursor = max(cursor, pend)
    if cursor < high:
        add(cursor, high)
    return regions


def choose_region(
    regions: Sequence[Region],
    required_mib: int = 0,
    *,
    start_mib: int | None = None,
) -> Region | None:
    """Pick a region, optionally the one starting at ``start_mib``."""

    if start_mib is not None:
        for region in regions:
            if region.start_mib == start_mib:
                return region
        return None
    candidates = [r for r in regions if r.size_mib >= required_mib]
    if not candidates:
        return None
    return max(candidates, key=lambda r: (r.size_mib, -r.start))


# ---------------------------------------------------------------------------
# Layout planning
# ---------------------------------------------------------------------------


def _new_partuuid() -> str:
    return str(uuid.uuid4()).upper()


def _new_fs_uuid() -> str:
    return str(uuid.uuid4()).lower()


def _new_fat_uuid() -> str:
    raw = uuid.uuid4().hex.upper()
    return raw[:4] + "-" + raw[4:8]


def _node_for(disk_path: str, number: int) -> str:
    # NVMe/mmcblk style device names need a "p" separator.
    if re.search(r"\d$", disk_path or ""):
        return f"{disk_path}p{number}"
    return f"{disk_path}{number}"


def _find_esp(partitions: Iterable[Partition]) -> Partition | None:
    for part in partitions:
        if (part.type or "").upper() == ESP_TYPE or (part.type or "").lower() == "ef":
            return part
    return None


def plan_layout(
    table: PartitionTable,
    region: Region,
    *,
    disk_path: str | None = None,
    esp_mib: int = ESP_MIB,
    root_mib: int | None = None,
    swap_mib: int | None = SWAP_MIB,
    root_min_mib: int = ROOT_MIN_MIB,
    reuse_existing_esp: bool = True,
    total_sectors: int | None = None,
    unit: int | None = None,
    uuid_factory: Callable[[], str] | None = None,
    delete_numbers: Sequence[int] = (),
) -> LayoutPlan:
    """Plan ESP/swap/root inside one free region.

    Existing partitions are preserved.  An existing ESP is reused unless
    ``reuse_existing_esp`` is false; otherwise a new 1 GiB ESP is placed at
    the start of the region.  Swap is 2 GiB when it fits next to the minimum
    root and is skipped with a warning otherwise.  Root grows to fill the
    remaining region unless ``root_mib`` is given.
    """

    sector_unit = unit or table.unit or 512
    if sector_unit <= 0:
        sector_unit = 512
    align = max(1, MIB // sector_unit)
    disk_path = disk_path or table.device
    total = total_sectors if total_sectors is not None else table.total_sectors
    if not disk_path:
        raise PlanError("disk path is required")

    if table.is_mbr or (table.label and not table.is_gpt):
        raise PlanError(
            "MBR disks are not supported by the Browneye installer; "
            "convert the disk to GPT first"
        )

    delete_numbers = tuple(sorted(set(int(n) for n in delete_numbers)))
    existing_numbers = {p.number for p in table.partitions}
    for number in delete_numbers:
        if number not in existing_numbers:
            raise PlanError(f"partition {number} does not exist on {disk_path}")

    remaining = table.without(delete_numbers)
    if region.start < 0 or region.end <= region.start:
        raise PlanError("invalid free region")
    if region.start % align or region.end % align or region.size % align:
        raise PlanError("free region is not 1 MiB aligned")
    if region.unit not in (0, sector_unit):
        raise PlanError("free region unit does not match the partition table")
    if total is not None and region.end > total:
        raise PlanError("free region extends past the end of the disk")

    low, high = _usable_bounds(table, total, sector_unit, align)
    if region.start < low or region.end > high:
        raise PlanError("free region lies outside the usable GPT area")

    first_lba = table.firstlba if table.firstlba is not None else align
    if table.lastlba is not None:
        last_lba = table.lastlba
    elif total is not None:
        last_lba = total - 34
    else:
        raise PlanError("cannot determine the last usable GPT LBA")

    warnings: list[str] = []
    used_numbers = {p.number for p in remaining.partitions}

    def take_number() -> int:
        for number in range(1, 129):
            if number not in used_numbers:
                used_numbers.add(number)
                return number
        raise PlanError("no free GPT partition numbers")

    new_uuid = uuid_factory or _new_partuuid

    existing_esp = _find_esp(remaining.partitions) if reuse_existing_esp else None
    cursor = region.start
    if existing_esp is not None:
        if (existing_esp.type or "").upper() != ESP_TYPE:
            raise PlanError("the only ESP found is not a GPT EFI System Partition")
        fstype = (existing_esp.fstype or "").lower()
        if fstype and fstype not in ("vfat", "fat", "fat32", "msdos"):
            raise PlanError(
                "the existing ESP at partition {} is {}, not FAT; delete it "
                "or format it before installing".format(
                    existing_esp.number, existing_esp.fstype
                )
            )
        if not fstype and not existing_esp.fs_uuid:
            raise PlanError(
                "the existing ESP at partition {} has no FAT filesystem; "
                "delete it or format it before installing".format(
                    existing_esp.number
                )
            )
        if existing_esp.end > region.start and existing_esp.start < region.end:
            raise PlanError("the existing ESP overlaps the selected free region")
        esp = PlannedPartition(
            role="esp",
            number=existing_esp.number,
            start=existing_esp.start,
            size=existing_esp.size,
            type=ESP_TYPE,
            partuuid=existing_esp.partuuid or "",
            fs_uuid=existing_esp.fs_uuid,
            name=existing_esp.name or "EFI System",
            existing=True,
            node=existing_esp.node,
        )
        if not esp.partuuid:
            raise PlanError("the existing ESP has no partition UUID")
        esp_mib_actual = (esp.size * sector_unit) // MIB
        if esp_mib_actual < 256:
            warnings.append(
                f"reusing a small existing ESP ({esp_mib_actual} MiB); "
                "the bootloader keeps the kernel and initramfs on the ESP, "
                "so 1 GiB is recommended"
            )
        if not esp.fs_uuid:
            warnings.append(
                "the existing ESP has no filesystem UUID; /boot will use PARTUUID"
            )
    else:
        if esp_mib < 32:
            raise PlanError("ESP must be at least 32 MiB")
        esp_sectors = (esp_mib * MIB) // sector_unit
        if esp_sectors * sector_unit != esp_mib * MIB:
            raise PlanError("ESP size is not a multiple of the logical sector size")
        if esp_sectors % align:
            raise PlanError("ESP size is not 1 MiB aligned")
        esp_end = region.start + esp_sectors
        if esp_end > region.end:
            raise PlanError(
                f"free region is too small for a {esp_mib} MiB ESP"
            )
        volid = uuid.uuid4().hex.upper()[:8]
        esp = PlannedPartition(
            role="esp",
            number=take_number(),
            start=region.start,
            size=esp_sectors,
            type=ESP_TYPE,
            partuuid=new_uuid(),
            fs_uuid=volid[:4] + "-" + volid[4:8],
            name="Browneye ESP",
            existing=False,
            node="",
        )
        cursor = esp_end

    root_min_sectors = (root_min_mib * MIB) // sector_unit
    available = region.end - cursor
    swap: PlannedPartition | None = None
    swap_sectors = 0
    if swap_mib is not None and swap_mib > 0:
        swap_sectors = (swap_mib * MIB) // sector_unit
        if swap_sectors * sector_unit != swap_mib * MIB:
            raise PlanError("swap size is not a multiple of the logical sector size")
        if available >= swap_sectors + root_min_sectors:
            swap = PlannedPartition(
                role="swap",
                number=take_number(),
                start=cursor,
                size=swap_sectors,
                type=LINUX_SWAP_TYPE,
                partuuid=new_uuid(),
                fs_uuid=_new_fs_uuid(),
                name="Browneye swap",
                existing=False,
                node=_node_for(disk_path, 0),
            )
            cursor += swap_sectors
            available = region.end - cursor
        else:
            available_mib = (available * sector_unit) // MIB
            warnings.append(
                "swap skipped: the free region leaves {} MiB after the ESP, "
                "but {} MiB swap + {} MiB root minimum are required".format(
                    available_mib, swap_mib, root_min_mib
                )
            )

    root_available = region.end - cursor
    if root_available < root_min_sectors:
        raise PlanError(
            "free region is too small: {} MiB available for root, "
            "{} MiB minimum".format(
                (root_available * sector_unit) // MIB, root_min_mib
            )
        )
    if root_mib is not None:
        root_sectors = (int(root_mib) * MIB) // sector_unit
        if root_sectors * sector_unit != int(root_mib) * MIB:
            raise PlanError("root size is not a multiple of the logical sector size")
        if root_sectors < root_min_sectors:
            raise PlanError(
                f"root must be at least {root_min_mib} MiB"
            )
        if root_sectors > root_available:
            raise PlanError(
                "root size {} MiB exceeds the {} MiB available in the region".format(
                    root_mib, (root_available * sector_unit) // MIB
                )
            )
    else:
        root_sectors = align_down(root_available, align)
        if root_sectors < root_min_sectors:
            raise PlanError(
                f"root must be at least {root_min_mib} MiB"
            )

    root = PlannedPartition(
        role="root",
        number=take_number(),
        start=cursor,
        size=root_sectors,
        type=LINUX_FS_TYPE,
        partuuid=new_uuid(),
        fs_uuid=_new_fs_uuid(),
        name="Browneye Linux",
        existing=False,
        node=_node_for(disk_path, 0),
    )
    leftover = region.end - root.end
    if leftover > 0:
        warnings.append(
            "{} MiB of the free region will be left unallocated".format(
                (leftover * sector_unit) // MIB
            )
        )

    # Fill in the node names now that numbers are known.
    esp = replace(esp, node=esp.node or _node_for(disk_path, esp.number))
    if swap is not None:
        swap = replace(swap, node=_node_for(disk_path, swap.number))
    root = replace(root, node=_node_for(disk_path, root.number))

    disk_id = table.id or str(uuid.uuid4()).upper()
    new_table = _render_table(
        disk_path=disk_path,
        disk_id=disk_id,
        first_lba=first_lba,
        last_lba=last_lba,
        unit=sector_unit,
        remaining=remaining,
        new_parts=[p for p in (esp if not esp.existing else None, swap, root) if p is not None],
        delete_numbers=delete_numbers,
    )
    plan = LayoutPlan(
        disk_path=disk_path,
        disk_id=disk_id,
        table=table,
        region=region,
        esp=esp,
        swap=swap,
        root=root,
        new_table_text=new_table,
        warnings=tuple(warnings),
        delete_numbers=delete_numbers,
        unit=sector_unit,
        total_sectors=total,
        first_lba=first_lba,
        last_lba=last_lba,
        root_min_mib=root_min_mib,
        esp_mib=esp_mib,
    )
    return plan


# ---------------------------------------------------------------------------
# Table rendering and verification
# ---------------------------------------------------------------------------


def _quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def _partition_line(
    disk_path: str,
    number: int,
    start: int,
    size: int,
    type_: str,
    partuuid: str | None,
    name: str | None,
    attrs: str | None,
    node: str | None = None,
) -> str:
    target = node or _node_for(disk_path, number)
    fields = ["start={}".format(start), "size={}".format(size)]
    fields.append("type={}".format((type_ or "").upper()))
    if partuuid:
        fields.append("uuid={}".format(partuuid))
    if name:
        fields.append("name={}".format(_quote(name)))
    if attrs:
        fields.append("attrs={}".format(_quote(attrs)))
    return "{} : {}".format(target, ", ".join(fields))


def _render_table(
    *,
    disk_path: str,
    disk_id: str,
    first_lba: int,
    last_lba: int,
    unit: int,
    remaining: PartitionTable,
    new_parts: Sequence[PlannedPartition],
    delete_numbers: Sequence[int],
) -> str:
    lines = [
        "label: gpt",
        "label-id: {}".format(disk_id),
        "unit: sectors",
        "first-lba: {}".format(first_lba),
        "last-lba: {}".format(last_lba),
        "sector-size: {}".format(unit),
        "",
    ]
    entries: list[tuple[int, str]] = []
    for part in remaining.partitions:
        entries.append(
            (
                part.number,
                _partition_line(
                    disk_path,
                    part.number,
                    part.start,
                    part.size,
                    part.type,
                    part.partuuid,
                    part.name,
                    part.attrs,
                    node=part.node or None,
                ),
            )
        )
    for part in new_parts:
        entries.append(
            (
                part.number,
                _partition_line(
                    disk_path,
                    part.number,
                    part.start,
                    part.size,
                    part.type,
                    part.partuuid,
                    part.name,
                    None,
                    node=part.node or None,
                ),
            )
        )
    entries.sort(key=lambda item: item[0])
    for _number, line in entries:
        lines.append(line)
    return "\n".join(lines) + "\n"


def render_table(plan: LayoutPlan) -> str:
    return plan.new_table_text


def verify_preserved(
    before: PartitionTable,
    after: PartitionTable,
    deleted: Sequence[int] = (),
    allowed_new: Sequence[int] = (),
) -> list[str]:
    """Return human-readable differences for partitions that must not change."""

    issues: list[str] = []
    deleted_set = set(deleted)
    allowed_set = set(allowed_new)

    if before.label is not None:
        if (before.label or "").lower() != (after.label or "").lower():
            issues.append(
                f"table label changed: {before.label!r} -> {after.label!r}"
            )
    if before.id and after.id and before.id.upper() != after.id.upper():
        issues.append(f"disk GUID changed: {before.id} -> {after.id}")
    for attr in ("firstlba", "lastlba", "unit"):
        old = getattr(before, attr)
        new = getattr(after, attr)
        if old is not None and new is not None and int(old) != int(new):
            issues.append(f"{attr} changed: {old} -> {new}")

    after_by_number = after.by_number()
    before_numbers = {p.number for p in before.partitions}
    for part in before.partitions:
        if part.number in deleted_set:
            continue
        other = after_by_number.get(part.number)
        if other is None:
            issues.append(f"partition {part.number} disappeared")
            continue
        for attr, label in (
            ("start", "start"),
            ("size", "size"),
            ("type", "type"),
            ("partuuid", "UUID"),
            ("name", "name"),
            ("attrs", "attrs"),
        ):
            old = getattr(part, attr)
            new = getattr(other, attr)
            if attr in ("type", "partuuid") and old and new:
                if str(old).upper() != str(new).upper():
                    issues.append(
                        f"partition {part.number} {label} changed: {old} -> {new}"
                    )
            elif old != new:
                issues.append(
                    f"partition {part.number} {label} changed: {old!r} -> {new!r}"
                )

    for part in after.partitions:
        if part.number in before_numbers:
            continue
        if part.number not in allowed_set:
            issues.append(
                f"unexpected new partition {part.number} at sector {part.start}"
            )

    for number in deleted_set:
        if number in after_by_number and number not in allowed_set:
            issues.append(f"partition {number} was not deleted")
    return issues


def verify_planned(plan: LayoutPlan, after: PartitionTable) -> list[str]:
    """Check that every planned new partition exists exactly as planned."""

    issues: list[str] = []
    after_by_number = after.by_number()
    for part in plan.new_partitions:
        other = after_by_number.get(part.number)
        if other is None:
            issues.append(
                f"planned partition {part.number} ({part.role}) is missing"
            )
            continue
        for attr, label in (
            ("start", "start"),
            ("size", "size"),
            ("type", "type"),
            ("partuuid", "UUID"),
        ):
            old = getattr(part, attr)
            new = getattr(other, attr)
            if attr in ("type", "partuuid") and old and new:
                if str(old).upper() != str(new).upper():
                    issues.append(
                        f"planned partition {part.number} ({part.role}) "
                        f"{label} changed: {old} -> {new}"
                    )
            elif old != new:
                issues.append(
                    f"planned partition {part.number} ({part.role}) "
                    f"{label} changed: {old!r} -> {new!r}"
                )
    return issues


def validate_plan(plan: LayoutPlan) -> list[str]:
    """Return a list of safety/size violations; an empty list is a valid plan."""

    issues: list[str] = []
    table = plan.table
    unit = plan.unit
    align = plan.align
    region = plan.region

    if table.label not in (None, "", "gpt"):
        issues.append("partition table is not GPT")
    if region.start % align or region.end % align:
        issues.append("region is not 1 MiB aligned")
    if region.end <= region.start:
        issues.append("region is empty")

    remaining = table.without(plan.delete_numbers)
    existing_by_number = {p.number: p for p in remaining.partitions}
    existing_spans = [(p.start, p.end, p.number) for p in remaining.partitions]
    new_numbers: set[int] = set()

    def check_part(part: PlannedPartition, expected_role: str, expected_type: str) -> None:
        if part.role != expected_role:
            issues.append(f"{expected_role}: wrong role {part.role}")
        if part.type.upper() != expected_type:
            issues.append(f"{expected_role}: wrong partition type {part.type}")
        if not part.existing:
            if part.start % align:
                issues.append(f"{expected_role}: start is not 1 MiB aligned")
            if part.size % align or part.size <= 0:
                issues.append(f"{expected_role}: size is not 1 MiB aligned")
            if not region.contains(part.start, part.size):
                issues.append(f"{expected_role}: outside the selected free region")
        if part.end > plan.last_lba + 1:
            issues.append(f"{expected_role}: overlaps the backup GPT")
        if not part.partuuid:
            issues.append(f"{expected_role}: missing partition UUID")
        if part.number < 1 or part.number > 128:
            issues.append(f"{expected_role}: invalid partition number {part.number}")
        if part.number in new_numbers:
            issues.append(f"{expected_role}: duplicate partition number {part.number}")
        new_numbers.add(part.number)
        if part.existing:
            old = existing_by_number.get(part.number)
            if old is None:
                issues.append(f"{expected_role}: existing partition is missing")
        else:
            if part.number in existing_by_number:
                issues.append(
                    f"{expected_role}: number {part.number} is already in use"
                )
            for start, end, number in existing_spans:
                if part.start < end and start < part.end:
                    issues.append(
                        f"{expected_role}: overlaps existing partition {number}"
                    )

    check_part(plan.esp, "esp", ESP_TYPE)
    if plan.swap is not None:
        check_part(plan.swap, "swap", LINUX_SWAP_TYPE)
    check_part(plan.root, "root", LINUX_FS_TYPE)

    root_min_sectors = (plan.root_min_mib * MIB) // unit
    if plan.root.size < root_min_sectors:
        issues.append(
            "root is smaller than {} MiB".format(plan.root_min_mib)
        )
    if not plan.esp.existing:
        esp_sectors = (plan.esp_mib * MIB) // unit
        if plan.esp.size != esp_sectors:
            issues.append("new ESP does not have the requested size")
        if plan.esp.start != region.start:
            issues.append("new ESP is not at the start of the free region")
    if plan.esp.existing:
        old = existing_by_number.get(plan.esp.number)
        if old is None:
            issues.append("reused ESP is not in the preserved table")
        elif (old.type or "").upper() != ESP_TYPE:
            issues.append("reused ESP is not a GPT EFI System Partition")

    # New partitions must not overlap each other.
    planned = [p for p in (plan.esp, plan.swap, plan.root) if p is not None]
    for index, first in enumerate(planned):
        for second in planned[index + 1 :]:
            if first.start < second.end and second.start < first.end:
                issues.append(
                    f"planned partitions {first.number} and {second.number} overlap"
                )

    if "label: gpt" not in plan.new_table_text.splitlines()[0:1]:
        issues.append("rendered table is not GPT")
    return issues


# ---------------------------------------------------------------------------
# Commands emitted for the command runner
# ---------------------------------------------------------------------------


def _safe_name(disk_path: str) -> str:
    name = os.path.basename(disk_path) or "disk"
    return re.sub(r"[^A-Za-z0-9_.-]", "_", name)


def backup_paths(plan: LayoutPlan, backup_dir: str = "/run/browneye/backup") -> tuple[str, str]:
    name = _safe_name(plan.disk_path)
    return (
        os.path.join(backup_dir, name + ".sfdisk"),
        os.path.join(backup_dir, name),
    )


def snapshot_commands(
    plan: LayoutPlan, backup_dir: str = "/run/browneye/backup"
) -> list[Command]:
    dump_path, prefix = backup_paths(plan, backup_dir)
    blank = plan.table.is_blank
    return [
        Command(
            argv=("mkdir", "-p", backup_dir),
            step="partition",
            description="create partition-table backup directory",
        ),
        Command(
            argv=("sfdisk", "--dump", plan.disk_path),
            step="partition",
            description="save the complete partition table before any change",
            stdout_path=dump_path,
            allow_failure=blank,
        ),
        Command(
            argv=(
                "sfdisk",
                "--backup-pt-sectors",
                "--backup-file",
                prefix,
                plan.disk_path,
            ),
            step="partition",
            description="save the binary primary/backup GPT sectors",
            allow_failure=blank,
        ),
    ]


def delete_commands(plan: LayoutPlan) -> list[Command]:
    commands: list[Command] = []
    for number in plan.delete_numbers:
        part = plan.table.find_number(number)
        node = (part.node if part else "") or _node_for(plan.disk_path, number)
        commands.append(
            Command(
                argv=("wipefs", "--all", "--force", node),
                step="partition",
                description=f"clear filesystem signatures on partition {number}",
            )
        )
        commands.append(
            Command(
                argv=("sfdisk", "--delete", "--no-reread", plan.disk_path, str(number)),
                step="partition",
                description=f"delete partition {number}",
            )
        )
    return commands


def reread_commands(plan: LayoutPlan, step: str = "partition") -> list[Command]:
    return [
        Command(
            argv=("blockdev", "--rereadpt", plan.disk_path),
            step=step,
            description="ask the kernel to reread the partition table",
            allow_failure=True,
        ),
        Command(
            argv=("partx", "-u", plan.disk_path),
            step=step,
            description="update in-kernel partition mappings",
            allow_failure=True,
        ),
        Command(
            argv=("udevadm", "settle", "--timeout=60"),
            step=step,
            description="wait for udev partition nodes",
        ),
    ]


def write_table_commands(plan: LayoutPlan) -> list[Command]:
    return [
        Command(
            argv=(
                "sfdisk",
                "--no-reread",
                "--lock=yes",
                plan.disk_path,
            ),
            step="partition",
            description="write the complete replacement GPT preserving other entries",
            stdin=plan.new_table_text,
            stdin_redacted=False,
        ),
        *reread_commands(plan),
        Command(
            argv=("sfdisk", "--verify", plan.disk_path),
            step="partition",
            description="verify the written GPT",
        ),
    ]


def partition_commands(
    plan: LayoutPlan, backup_dir: str = "/run/browneye/backup"
) -> list[Command]:
    return snapshot_commands(plan, backup_dir) + delete_commands(plan) + write_table_commands(plan)


def format_commands(plan: LayoutPlan) -> list[Command]:
    commands: list[Command] = []
    if not plan.esp.existing:
        argv = [
            "mkfs.fat",
            "-F",
            "32",
            "-n",
            "BROWNEYEESP",
        ]
        if plan.unit == 4096:
            # The FAT BPB must match 4Kn logical sectors.
            argv.extend(["-S", "4096"])
        if plan.esp.fat_volume_id:
            argv.extend(["-i", plan.esp.fat_volume_id])
        argv.append(plan.esp.by_partuuid)
        commands.append(
            Command(
                argv=tuple(argv),
                step="format",
                description="create the FAT32 EFI System Partition",
            )
        )
    root_argv = [
        "mke2fs",
        "-t",
        "ext4",
        "-F",
        "-L",
        "browneye",
        "-m",
        "1",
    ]
    if plan.root.fs_uuid:
        root_argv.extend(["-U", plan.root.fs_uuid])
    root_argv.extend(
        [
            "-E",
            "lazy_itable_init=0,lazy_journal_init=0,nodiscard",
            plan.root.by_partuuid,
        ]
    )
    commands.append(
        Command(
            argv=tuple(root_argv),
            step="format",
            description="create the ext4 root filesystem",
        )
    )
    if plan.swap is not None:
        swap_argv = ["mkswap", "-L", "browneye-swap"]
        if plan.swap.fs_uuid:
            swap_argv.extend(["-U", plan.swap.fs_uuid])
        swap_argv.append(plan.swap.by_partuuid)
        commands.append(
            Command(
                argv=tuple(swap_argv),
                step="format",
                description="create the swap area",
            )
        )
    return commands


def format_verify_commands(plan: LayoutPlan) -> list[Command]:
    commands = [
        Command(
            argv=("blkid", "-p", "-s", "TYPE", "-o", "value", plan.esp.by_partuuid),
            step="format",
            description="verify the ESP filesystem type",
            read_only=True,
            destructive=False,
        ),
        Command(
            argv=("blkid", "-p", "-s", "UUID", "-o", "value", plan.esp.by_partuuid),
            step="format",
            description="verify the ESP UUID",
            read_only=True,
            destructive=False,
        ),
        Command(
            argv=("blkid", "-p", "-s", "TYPE", "-o", "value", plan.root.by_partuuid),
            step="format",
            description="verify the root filesystem type",
            read_only=True,
            destructive=False,
        ),
        Command(
            argv=("blkid", "-p", "-s", "UUID", "-o", "value", plan.root.by_partuuid),
            step="format",
            description="verify the root filesystem UUID",
            read_only=True,
            destructive=False,
        ),
    ]
    if plan.swap is not None:
        commands.append(
            Command(
                argv=("blkid", "-p", "-s", "TYPE", "-o", "value", plan.swap.by_partuuid),
                step="format",
                description="verify the swap type",
                read_only=True,
                destructive=False,
            )
        )
    return commands


def rollback_commands(
    plan: LayoutPlan, backup_dir: str = "/run/browneye/backup"
) -> list[Command]:
    dump_path, _prefix = backup_paths(plan, backup_dir)
    return [
        Command(
            argv=("sfdisk", "--no-reread", plan.disk_path),
            step="partition",
            description="restore the saved partition table after a verification failure",
            stdin_path=dump_path,
            stdin_redacted=False,
        ),
        *reread_commands(plan),
        Command(
            argv=("sfdisk", "--verify", plan.disk_path),
            step="partition",
            description="verify the restored GPT",
        ),
    ]


def disk_commands(
    plan: LayoutPlan, backup_dir: str = "/run/browneye/backup"
) -> list[Command]:
    """The complete disk phase (partition + format) for a dry-run plan."""

    return partition_commands(plan, backup_dir) + format_commands(plan)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def type_name(type_value: str | None, mbr: bool = False) -> str:
    text = (type_value or "").strip()
    if not text:
        return "unknown"
    if mbr:
        return MBR_TYPE_NAMES.get(text.lower(), text)
    return GPT_TYPE_NAMES.get(text.upper(), text)


def human_size(size_bytes: int) -> str:
    value = float(size_bytes)
    for suffix in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(value) < 1024 or suffix == "TiB":
            if suffix == "B":
                return f"{int(value)} {suffix}"
            return f"{value:.1f} {suffix}"
        value /= 1024
    return f"{value:.1f} TiB"


def region_human(region: Region) -> str:
    return "{} MiB .. {} MiB ({} MiB)".format(
        region.start_mib, region.end_mib, region.size_mib
    )
