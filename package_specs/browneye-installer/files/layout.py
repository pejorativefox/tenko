"""Multi-disk partition and mount-point planning.

The installer used to plan exactly one disk with an ESP, swap and root.  This
module generalises that model:

* a :class:`PartitionSpec` describes one partition the user wants (a newly
  created partition, or an existing partition that should be adopted without
  formatting);
* a :class:`DiskSpec` groups the edits for one disk;
* :func:`plan_disk` turns one ``DiskSpec`` plus a parsed partition table into
  a :class:`DiskLayout` (complete replacement table, planned partitions);
* an :class:`InstallLayout` groups several ``DiskLayout`` objects, enforces
  the system-wide rules (one ``/``, one ESP, unique mount points) and knows
  how to mount and describe the result.

The module is pure: it parses nothing and executes nothing, so the whole
layout can be built and validated in unit tests without root or a disk.
"""

from __future__ import annotations

import os
import re
import uuid
from dataclasses import dataclass
from typing import Any, Sequence

import disk
from runner import Command

MIB = disk.MIB
GIB = disk.GIB

ESP_MIB = 1024
SWAP_MIB = 2048
ROOT_MIN_MIB = 8192
ESP_MIN_MIB = 32
ESP_RECOMMENDED_MIB = 256

ROLES = ("esp", "swap", "root", "data")
FORMATTABLE_FSTYPES = ("ext4", "btrfs", "vfat", "swap")
DATA_FSTYPES = ("ext4", "btrfs", "vfat")

# Mount points the target system already owns; data partitions below these
# would be shadowed by the bind mounts or by systemd.
RESERVED_MOUNTS = ("/proc", "/sys", "/dev", "/run", "/tmp")
RESERVED_PREFIXES = ("/proc/", "/sys/", "/dev/", "/run/")

PlanError = disk.PlanError

_LABEL_MAX = 16
_FAT_LABEL_MAX = 11


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PartitionSpec:
    """One requested partition.

    ``existing_number`` adopts an existing table entry; in that case
    ``size_mib`` and ``region_start_mib`` are ignored.  ``format`` says
    whether an adopted entry is also reformatted.  A newly created partition
    always gets a fresh filesystem.
    """

    role: str
    fstype: str
    mountpoint: str | None = None
    size_mib: int | None = None
    region_start_mib: int | None = None
    existing_number: int | None = None
    format: bool = True
    name: str | None = None
    label: str | None = None

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.role not in ROLES:
            issues.append("partition role must be one of " + ", ".join(ROLES))
        if self.fstype not in FORMATTABLE_FSTYPES:
            issues.append(
                "filesystem must be one of " + ", ".join(FORMATTABLE_FSTYPES)
            )
        if self.role == "esp":
            if self.fstype != "vfat":
                issues.append("the EFI System Partition must be vfat")
            if self.mountpoint != "/boot":
                issues.append("the ESP must be mounted at /boot")
        elif self.role == "swap":
            if self.fstype != "swap":
                issues.append("swap partitions must use the swap filesystem")
            if self.mountpoint:
                issues.append("swap partitions have no mount point")
        elif self.role == "root":
            if self.mountpoint != "/":
                issues.append("the root partition must be mounted at /")
            if self.fstype not in ("ext4", "btrfs"):
                issues.append("the root filesystem must be ext4 or btrfs")
        elif self.role == "data":
            if self.fstype not in DATA_FSTYPES:
                issues.append(
                    "data partitions must use ext4, btrfs or vfat"
                )
            if not self.mountpoint or not self.mountpoint.startswith("/"):
                issues.append("data partitions need an absolute mount point")
            elif not re.fullmatch(r"/[A-Za-z0-9._/-]+", self.mountpoint):
                issues.append(
                    "mount point may contain only letters, digits, '.', '_', '-' "
                    "and '/'"
                )
            elif self.mountpoint == "/":
                issues.append("a data partition cannot be mounted at /")
            elif self.mountpoint == "/boot":
                issues.append("use an esp role for the /boot partition")
            elif any(
                self.mountpoint == item or self.mountpoint.startswith(item + "/")
                for item in RESERVED_MOUNTS
            ) or any(self.mountpoint.startswith(prefix) for prefix in RESERVED_PREFIXES):
                issues.append(
                    "mount point {} is reserved by the system".format(
                        self.mountpoint
                    )
                )
        if self.size_mib is not None:
            try:
                size = int(self.size_mib)
            except (TypeError, ValueError):
                issues.append("partition size must be an integer number of MiB")
            else:
                if size <= 0:
                    issues.append("partition size must be positive")
                elif self.existing_number is None:
                    minimum = {"btrfs": 256, "ext4": 16, "vfat": 32}.get(
                        self.fstype
                    )
                    if minimum is not None and size < minimum:
                        issues.append(
                            "{} partitions must be at least {} MiB".format(
                                self.fstype, minimum
                            )
                        )
        if self.region_start_mib is not None and int(self.region_start_mib) < 0:
            issues.append("region start must not be negative")
        if self.existing_number is not None:
            try:
                number = int(self.existing_number)
            except (TypeError, ValueError):
                issues.append("existing partition number must be an integer")
            else:
                if number < 1:
                    issues.append("existing partition numbers must be positive")
        return issues

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "role": self.role,
            "fstype": self.fstype,
            "mountpoint": self.mountpoint,
            "format": self.format,
        }
        if self.size_mib is not None:
            payload["size_mib"] = self.size_mib
        if self.region_start_mib is not None:
            payload["region_start_mib"] = self.region_start_mib
        if self.existing_number is not None:
            payload["existing_number"] = self.existing_number
        if self.name:
            payload["name"] = self.name
        if self.label:
            payload["label"] = self.label
        return payload


@dataclass(frozen=True)
class DiskSpec:
    path: str
    serial: str | None = None
    size_bytes: int | None = None
    model: str | None = None
    delete_partitions: tuple[int, ...] = ()
    partitions: tuple[PartitionSpec, ...] = ()

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.path or not self.path.startswith("/dev/"):
            issues.append("disk path must be an absolute /dev/... path")
        if len(set(self.delete_partitions)) != len(self.delete_partitions):
            issues.append("delete_partitions contains duplicates")
        if any(int(number) < 1 for number in self.delete_partitions):
            issues.append("delete_partitions entries must be positive")
        for index, part in enumerate(self.partitions, 1):
            for issue in part.validate():
                issues.append("partition {}: {}".format(index, issue))
        adopted = [
            part.existing_number
            for part in self.partitions
            if part.existing_number is not None
        ]
        if len(set(adopted)) != len(adopted):
            issues.append("the same existing partition is assigned twice")
        if set(adopted) & set(self.delete_partitions):
            issues.append("a partition cannot be both deleted and assigned")
        return issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "serial": self.serial,
            "size_bytes": self.size_bytes,
            "model": self.model,
            "delete_partitions": list(self.delete_partitions),
            "partitions": [part.to_dict() for part in self.partitions],
        }


@dataclass(frozen=True)
class InstallSpec:
    disks: tuple[DiskSpec, ...] = ()

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.disks:
            issues.append("the layout needs at least one disk")
        paths = [item.path for item in self.disks]
        if len(set(paths)) != len(paths):
            issues.append("a disk appears more than once")
        roots = 0
        esps = 0
        mounts: dict[str, str] = {}
        for item in self.disks:
            issues.extend(item.validate())
            for part in item.partitions:
                if part.role == "root":
                    roots += 1
                elif part.role == "esp":
                    esps += 1
                if part.mountpoint:
                    if part.mountpoint in mounts:
                        issues.append(
                            "mount point {} is assigned twice ({} and {})".format(
                                part.mountpoint, mounts[part.mountpoint], item.path
                            )
                        )
                    mounts[part.mountpoint] = item.path
        if self.disks:
            if roots != 1:
                issues.append("the layout must have exactly one root partition")
            if esps != 1:
                issues.append(
                    "the layout must have exactly one EFI System Partition"
                )
        return issues

    def to_dict(self) -> dict[str, Any]:
        return {"disks": [item.to_dict() for item in self.disks]}

    @classmethod
    def from_mapping(cls, data: Any) -> "InstallSpec":
        if not isinstance(data, dict):
            raise ValueError("layout must be a JSON object")
        unknown = set(data) - {"disks"}
        if unknown:
            raise ValueError(
                "unknown layout keys: " + ", ".join(sorted(unknown))
            )
        raw_disks = data.get("disks")
        if not isinstance(raw_disks, list) or not raw_disks:
            raise ValueError("layout.disks must be a non-empty list")
        disks: list[DiskSpec] = []
        for index, raw_disk in enumerate(raw_disks, 1):
            disks.append(_disk_spec_from_mapping(raw_disk, index))
        return cls(disks=tuple(disks))


def _int(value: Any, what: str) -> int:
    if isinstance(value, bool):
        raise ValueError(what + " must be an integer")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(what + " must be an integer") from exc


def _disk_spec_from_mapping(raw: Any, index: int) -> DiskSpec:
    if not isinstance(raw, dict):
        raise ValueError("disk {} must be an object".format(index))
    unknown = set(raw) - {
        "path",
        "serial",
        "size_bytes",
        "model",
        "delete_partitions",
        "partitions",
    }
    if unknown:
        raise ValueError(
            "unknown keys for disk {}: {}".format(
                index, ", ".join(sorted(unknown))
            )
        )
    path = raw.get("path")
    if not isinstance(path, str) or not path.startswith("/dev/"):
        raise ValueError("disk {}.path must be an absolute /dev/... path".format(index))
    delete = raw.get("delete_partitions") or []
    if not isinstance(delete, list):
        raise ValueError("disk {}.delete_partitions must be a list".format(index))
    partitions: list[PartitionSpec] = []
    raw_parts = raw.get("partitions") or []
    if not isinstance(raw_parts, list):
        raise ValueError("disk {}.partitions must be a list".format(index))
    for part_index, raw_part in enumerate(raw_parts, 1):
        partitions.append(_partition_from_mapping(raw_part, index, part_index))
    size = raw.get("size_bytes")
    return DiskSpec(
        path=path,
        serial=raw.get("serial"),
        size_bytes=_int(size, "size_bytes") if size is not None else None,
        model=raw.get("model"),
        delete_partitions=tuple(_int(item, "partition number") for item in delete),
        partitions=tuple(partitions),
    )


def _partition_from_mapping(raw: Any, disk_index: int, part_index: int) -> PartitionSpec:
    label = "disk {}, partition {}".format(disk_index, part_index)
    if not isinstance(raw, dict):
        raise ValueError(label + " must be an object")
    unknown = set(raw) - {
        "role",
        "fstype",
        "mountpoint",
        "size_mib",
        "region_start_mib",
        "existing_number",
        "format",
        "name",
        "label",
    }
    if unknown:
        raise ValueError(
            "{} has unknown keys: {}".format(label, ", ".join(sorted(unknown)))
        )
    role = str(raw.get("role", "data"))
    fstype = str(raw.get("fstype", "ext4"))
    mountpoint = raw.get("mountpoint")
    if mountpoint is not None and not isinstance(mountpoint, str):
        raise ValueError(label + ".mountpoint must be a string or null")
    size = raw.get("size_mib")
    region = raw.get("region_start_mib")
    existing = raw.get("existing_number")
    format_value = raw.get("format")
    if format_value is None:
        # Adopting an existing entry keeps its data unless format is explicit.
        format_value = existing is None
    if not isinstance(format_value, bool):
        raise ValueError(label + ".format must be true or false")
    spec = PartitionSpec(
        role=role,
        fstype=fstype,
        mountpoint=mountpoint,
        size_mib=_int(size, label + ".size_mib") if size is not None else None,
        region_start_mib=(
            _int(region, label + ".region_start_mib")
            if region is not None
            else None
        ),
        existing_number=(
            _int(existing, label + ".existing_number")
            if existing is not None
            else None
        ),
        format=bool(format_value),
        name=raw.get("name"),
        label=raw.get("label"),
    )
    issues = spec.validate()
    if issues:
        raise ValueError(label + ": " + "; ".join(issues))
    return spec


# ---------------------------------------------------------------------------
# Planned layout
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DiskLayout:
    disk_path: str
    disk_id: str
    table: disk.PartitionTable
    unit: int
    total_sectors: int | None
    first_lba: int
    last_lba: int
    delete_numbers: tuple[int, ...]
    partitions: tuple[disk.PlannedPartition, ...]
    new_table_text: str
    warnings: tuple[str, ...] = ()
    regions: tuple[disk.Region, ...] = ()

    @property
    def new_partitions(self) -> tuple[disk.PlannedPartition, ...]:
        return tuple(part for part in self.partitions if not part.existing)

    @property
    def changed(self) -> bool:
        return bool(self.new_partitions or self.delete_numbers)

    @property
    def esp(self) -> disk.PlannedPartition | None:
        return next((part for part in self.partitions if part.role == "esp"), None)

    @property
    def root(self) -> disk.PlannedPartition | None:
        return next((part for part in self.partitions if part.role == "root"), None)

    @property
    def swaps(self) -> tuple[disk.PlannedPartition, ...]:
        return tuple(part for part in self.partitions if part.role == "swap")

    @property
    def swap(self) -> disk.PlannedPartition | None:
        return self.swaps[0] if self.swaps else None

    @property
    def data(self) -> tuple[disk.PlannedPartition, ...]:
        return tuple(part for part in self.partitions if part.role == "data")

    def part_for_number(self, number: int) -> disk.PlannedPartition | None:
        return next((part for part in self.partitions if part.number == number), None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "disk": self.disk_path,
            "disk_id": self.disk_id,
            "unit": self.unit,
            "first_lba": self.first_lba,
            "last_lba": self.last_lba,
            "delete_partitions": list(self.delete_numbers),
            "regions": [
                {
                    "start_mib": region.start_mib,
                    "end_mib": region.end_mib,
                    "size_mib": region.size_mib,
                }
                for region in self.regions
            ],
            "partitions": [_planned_dict(part) for part in self.partitions],
            "warnings": list(self.warnings),
            "table": self.new_table_text,
        }


def _planned_dict(part: disk.PlannedPartition | None) -> dict[str, Any] | None:
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
        "mountpoint": part.mountpoint,
        "fstype": part.fstype,
        "format": part.format,
        "node": part.node,
    }


@dataclass(frozen=True)
class InstallLayout:
    disks: tuple[DiskLayout, ...]

    @property
    def partitions(self) -> tuple[disk.PlannedPartition, ...]:
        return tuple(part for item in self.disks for part in item.partitions)

    @property
    def new_partitions(self) -> tuple[disk.PlannedPartition, ...]:
        return tuple(part for item in self.disks for part in item.new_partitions)

    @property
    def root(self) -> disk.PlannedPartition | None:
        return next((part for part in self.partitions if part.role == "root"), None)

    @property
    def esp(self) -> disk.PlannedPartition | None:
        return next((part for part in self.partitions if part.role == "esp"), None)

    @property
    def swaps(self) -> tuple[disk.PlannedPartition, ...]:
        return tuple(part for part in self.partitions if part.role == "swap")

    @property
    def swap(self) -> disk.PlannedPartition | None:
        return self.swaps[0] if self.swaps else None

    @property
    def data(self) -> tuple[disk.PlannedPartition, ...]:
        return tuple(part for part in self.partitions if part.role == "data")

    @property
    def mounts(self) -> tuple[disk.PlannedPartition, ...]:
        return tuple(
            part
            for part in self.partitions
            if part.mountpoint and part.role != "swap"
        )

    def disk_for(self, part: disk.PlannedPartition) -> DiskLayout | None:
        for item in self.disks:
            if part in item.partitions:
                return item
        return None

    def find_mount(self, mountpoint: str) -> disk.PlannedPartition | None:
        return next(
            (part for part in self.partitions if part.mountpoint == mountpoint),
            None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {"disks": [item.to_dict() for item in self.disks]}


# ---------------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------------


def _new_partuuid() -> str:
    return str(uuid.uuid4()).upper()


def _new_fs_uuid() -> str:
    return str(uuid.uuid4()).lower()


def _new_fat_uuid() -> str:
    raw = uuid.uuid4().hex.upper()
    return raw[:4] + "-" + raw[4:8]


def _label_for(role: str, mountpoint: str | None, fstype: str) -> str:
    if role == "esp":
        return "BROWNEYEESP"
    if role == "swap":
        return "browneye-swap"
    if role == "root":
        return "browneye"
    base = "browneye"
    if mountpoint:
        suffix = re.sub(r"[^A-Za-z0-9]+", "", mountpoint.strip("/")).lower()
        if suffix:
            base = "browneye-" + suffix
    limit = _FAT_LABEL_MAX if fstype == "vfat" else _LABEL_MAX
    return base[:limit]


def _plan_existing(
    spec: PartitionSpec,
    remaining: disk.PartitionTable,
) -> disk.PlannedPartition:
    number = int(spec.existing_number or 0)
    part = remaining.find_number(number)
    if part is None:
        raise PlanError("partition {} does not exist".format(number))
    if not part.partuuid:
        raise PlanError("partition {} has no partition UUID".format(number))
    fstype = spec.fstype
    actual = (part.fstype or "").lower()
    if spec.role == "esp":
        if actual and actual not in ("vfat", "fat", "fat32", "msdos"):
            raise PlanError(
                "the existing ESP at partition {} is {}, not FAT".format(
                    number, part.fstype
                )
            )
        if not actual and not part.fs_uuid:
            raise PlanError(
                "the existing ESP at partition {} has no FAT filesystem".format(
                    number
                )
            )
        fstype = "vfat"
    elif spec.role == "swap":
        if actual and actual != "swap":
            raise PlanError(
                "partition {} is {}, not a swap area".format(number, part.fstype)
            )
        if not spec.format and not actual:
            raise PlanError(
                "partition {} has no swap signature; format it or create a "
                "new swap partition".format(number)
            )
        fstype = "swap"
    else:
        detected = actual
        if detected in ("fat", "fat32", "msdos"):
            detected = "vfat"
        if not spec.format:
            if detected and detected not in ("ext4", "btrfs", "vfat"):
                raise PlanError(
                    "partition {} has unsupported filesystem {}".format(
                        number, part.fstype
                    )
                )
            if not detected:
                raise PlanError(
                    "partition {} has no readable filesystem; format it or "
                    "create a new partition instead".format(number)
                )
            if spec.fstype and spec.fstype != detected:
                raise PlanError(
                    "partition {} is {}, but the layout says {}".format(
                        number, detected, spec.fstype
                    )
                )
            fstype = detected
    if spec.role == "esp":
        new_fs_uuid = _new_fat_uuid()
    else:
        new_fs_uuid = _new_fs_uuid()
    return disk.PlannedPartition(
        role=spec.role,
        number=number,
        start=part.start,
        size=part.size,
        type=part.type,
        partuuid=part.partuuid,
        fs_uuid=part.fs_uuid or (new_fs_uuid if spec.format else None),
        name=spec.name or part.name or _label_for(spec.role, spec.mountpoint, fstype),
        existing=True,
        node=part.node,
        mountpoint=spec.mountpoint,
        fstype=fstype,
        format=spec.format,
        label=spec.label or _label_for(spec.role, spec.mountpoint, fstype),
    )


def plan_disk(
    table: disk.PartitionTable,
    spec: DiskSpec,
    *,
    disk_path: str | None = None,
    total_sectors: int | None = None,
    unit: int | None = None,
    root_min_mib: int = ROOT_MIN_MIB,
) -> DiskLayout:
    """Plan every requested change for one disk."""

    issues = spec.validate()
    if issues:
        raise PlanError("; ".join(issues))
    disk_path = disk_path or spec.path or table.device
    if not disk_path:
        raise PlanError("disk path is required")
    sector_unit = unit or table.unit or 512
    if sector_unit <= 0:
        sector_unit = 512
    align = max(1, MIB // sector_unit)
    total = total_sectors if total_sectors is not None else table.total_sectors

    if table.is_mbr or (table.label and not table.is_gpt):
        raise PlanError(
            "MBR disks are not supported by the Browneye installer; "
            "convert the disk to GPT first"
        )

    delete_numbers = tuple(sorted(set(int(n) for n in spec.delete_partitions)))
    existing_numbers = {part.number for part in table.partitions}
    for number in delete_numbers:
        if number not in existing_numbers:
            raise PlanError(
                "partition {} does not exist on {}".format(number, disk_path)
            )

    remaining = table.without(delete_numbers)

    first_lba = table.firstlba if table.firstlba is not None else align
    if table.lastlba is not None:
        last_lba = table.lastlba
    elif total is not None:
        last_lba = total - 34
    else:
        raise PlanError("cannot determine the last usable GPT LBA")

    warnings: list[str] = []
    used_numbers = {part.number for part in remaining.partitions}

    def take_number() -> int:
        for number in range(1, 129):
            if number not in used_numbers:
                used_numbers.add(number)
                return number
        raise PlanError("no free GPT partition numbers")

    regions = disk.find_free_regions(
        remaining,
        total_sectors=total,
        unit=sector_unit,
        align=align,
    )

    planned: list[disk.PlannedPartition] = []
    for request in spec.partitions:
        if request.existing_number is not None:
            part = _plan_existing(request, remaining)
            if part.number in {item.number for item in planned}:
                raise PlanError(
                    "partition {} is assigned more than once".format(part.number)
                )
            planned.append(part)

    new_requests = [
        request for request in spec.partitions if request.existing_number is None
    ]
    cursors: dict[int, int] = {}
    current_region: disk.Region | None = None

    def pick_region(required: int, request: PartitionSpec) -> disk.Region:
        nonlocal current_region
        if request.region_start_mib is not None:
            for region in regions:
                if region.start_mib == request.region_start_mib:
                    current_region = region
                    return region
            raise PlanError(
                "no free region starts at {} MiB on {}".format(
                    request.region_start_mib, disk_path
                )
            )
        if current_region is not None:
            return current_region
        candidates = [
            region for region in regions if required <= 0 or region.size >= required
        ]
        if not candidates:
            raise PlanError(
                "{} has no free region large enough for the requested layout".format(
                    disk_path
                )
            )
        current_region = max(candidates, key=lambda region: (region.size, -region.start))
        return current_region

    for request in new_requests:
        if request.size_mib is not None:
            size_sectors = (int(request.size_mib) * MIB) // sector_unit
            if size_sectors * sector_unit != int(request.size_mib) * MIB:
                raise PlanError(
                    "partition size is not a multiple of the logical sector size"
                )
            if request.role == "esp" and int(request.size_mib) < ESP_MIN_MIB:
                raise PlanError(
                    "the ESP must be at least {} MiB".format(ESP_MIN_MIB)
                )
            if request.role == "root" and int(request.size_mib) < root_min_mib:
                raise PlanError(
                    "root must be at least {} MiB".format(root_min_mib)
                )
        else:
            size_sectors = 0

        region = pick_region(size_sectors, request)
        start = cursors.get(region.start, region.start)
        if start % align:
            start = disk.align_up(start, align)
        available = region.end - start
        if available <= 0:
            raise PlanError(
                "the free region at {} MiB is full; add another region or "
                "reduce a partition".format(region.start_mib)
            )
        if request.size_mib is None:
            size_sectors = disk.align_down(available, align)
            if size_sectors <= 0:
                raise PlanError(
                    "no space left in the region at {} MiB".format(
                        region.start_mib
                    )
                )
            if request.role == "root" and (
                size_sectors * sector_unit // MIB
            ) < root_min_mib:
                raise PlanError(
                    "the free region leaves {} MiB for root, but {} MiB is "
                    "required".format(
                        (size_sectors * sector_unit) // MIB, root_min_mib
                    )
                )
        if size_sectors > available:
            raise PlanError(
                "a {} MiB partition does not fit in the {} MiB left in the "
                "region at {} MiB".format(
                    request.size_mib,
                    (available * sector_unit) // MIB,
                    region.start_mib,
                )
            )
        if size_sectors % align:
            raise PlanError("partition size is not 1 MiB aligned")

        number = take_number()
        if request.role == "esp":
            part_type = disk.ESP_TYPE
            fs_uuid = _new_fat_uuid()
        elif request.role == "swap":
            part_type = disk.LINUX_SWAP_TYPE
            fs_uuid = _new_fs_uuid()
        else:
            part_type = disk.LINUX_FS_TYPE
            fs_uuid = _new_fs_uuid()
        label = request.label or _label_for(
            request.role, request.mountpoint, request.fstype
        )
        planned.append(
            disk.PlannedPartition(
                role=request.role,
                number=number,
                start=start,
                size=size_sectors,
                type=part_type,
                partuuid=_new_partuuid(),
                fs_uuid=fs_uuid,
                name=request.name
                or (
                    "Browneye ESP"
                    if request.role == "esp"
                    else "Browneye swap"
                    if request.role == "swap"
                    else "Browneye Linux"
                ),
                existing=False,
                node=disk._node_for(disk_path, number),
                mountpoint=request.mountpoint,
                fstype=request.fstype,
                format=True,
                label=label,
            )
        )
        cursors[region.start] = start + size_sectors
        if request.size_mib is None:
            # A fill partition consumes the rest of its region.
            cursors[region.start] = region.end

    for region in regions:
        cursor = cursors.get(region.start, region.start)
        if cursor < region.end and any(
            part.start >= region.start and part.start < region.end
            for part in planned
            if not part.existing
        ):
            leftovers = ((region.end - cursor) * sector_unit) // MIB
            if leftovers >= 1:
                warnings.append(
                    "{} MiB of the free region at {} MiB will be left "
                    "unallocated".format(leftovers, region.start_mib)
                )

    for part in planned:
        if part.role == "esp" and part.existing:
            size_mib = (part.size * sector_unit) // MIB
            if size_mib < ESP_RECOMMENDED_MIB:
                warnings.append(
                    "reusing a small existing ESP ({} MiB); the bootloader "
                    "keeps the kernel and initramfs on the ESP, so 1 GiB is "
                    "recommended".format(size_mib)
                )
            if not part.fs_uuid:
                warnings.append(
                    "the existing ESP has no filesystem UUID; /boot will use "
                    "PARTUUID"
                )
        if part.end > last_lba + 1:
            raise PlanError("partition {} overlaps the backup GPT".format(part.number))

    disk_id = table.id or str(uuid.uuid4()).upper()
    if planned or delete_numbers:
        new_table = disk.render_new_table(
            disk_path=disk_path,
            disk_id=disk_id,
            first_lba=first_lba,
            last_lba=last_lba,
            unit=sector_unit,
            remaining=remaining,
            new_parts=[part for part in planned if not part.existing],
            delete_numbers=delete_numbers,
        )
    else:
        new_table = ""

    return DiskLayout(
        disk_path=disk_path,
        disk_id=disk_id,
        table=table,
        unit=sector_unit,
        total_sectors=total,
        first_lba=first_lba,
        last_lba=last_lba,
        delete_numbers=delete_numbers,
        partitions=tuple(sorted(planned, key=lambda part: part.number)),
        new_table_text=new_table,
        warnings=tuple(warnings),
        regions=tuple(regions),
    )


def plan_install(
    tables: dict[str, disk.PartitionTable],
    spec: InstallSpec,
    *,
    total_sectors: dict[str, int | None] | None = None,
    root_min_mib: int = ROOT_MIN_MIB,
) -> InstallLayout:
    """Plan all disks and enforce the system-wide invariants."""

    issues = spec.validate()
    if issues:
        raise PlanError("; ".join(issues))
    layouts: list[DiskLayout] = []
    for item in spec.disks:
        table = tables.get(item.path)
        if table is None:
            raise PlanError("no partition table was read for {}".format(item.path))
        layouts.append(
            plan_disk(
                table,
                item,
                disk_path=item.path,
                total_sectors=(total_sectors or {}).get(item.path),
                unit=table.unit,
                root_min_mib=root_min_mib,
            )
        )
    layout = InstallLayout(disks=tuple(layouts))
    issues = validate_layout(layout)
    if issues:
        raise PlanError("; ".join(issues))
    return layout


def validate_layout(layout: InstallLayout) -> list[str]:
    issues: list[str] = []
    roots = [part for part in layout.partitions if part.role == "root"]
    esps = [part for part in layout.partitions if part.role == "esp"]
    if len(roots) != 1:
        issues.append("the layout must have exactly one root partition")
    if len(esps) != 1:
        issues.append("the layout must have exactly one EFI System Partition")
    if roots:
        if roots[0].mountpoint != "/":
            issues.append("the root partition must be mounted at /")
        if (roots[0].size * _unit_for(layout, roots[0])) // MIB < ROOT_MIN_MIB:
            if not roots[0].existing:
                issues.append(
                    "root is smaller than {} MiB".format(ROOT_MIN_MIB)
                )
    if esps and esps[0].mountpoint != "/boot":
        issues.append("the ESP must be mounted at /boot")

    seen_mounts: set[str] = set()
    seen_numbers: set[tuple[str, int]] = set()
    seen_partuuids: set[str] = set()
    for item in layout.disks:
        for part in item.partitions:
            key = (item.disk_path, part.number)
            if key in seen_numbers:
                issues.append(
                    "partition {} on {} is planned twice".format(
                        part.number, item.disk_path
                    )
                )
            seen_numbers.add(key)
            if part.partuuid:
                lower = part.partuuid.lower()
                if lower in seen_partuuids:
                    issues.append(
                        "partition UUID {} is used twice".format(part.partuuid)
                    )
                seen_partuuids.add(lower)
            if part.mountpoint:
                if part.mountpoint in seen_mounts:
                    issues.append(
                        "mount point {} is assigned twice".format(part.mountpoint)
                    )
                seen_mounts.add(part.mountpoint)
                if part.mountpoint != "/" and not part.mountpoint.startswith("/"):
                    issues.append(
                        "mount point {} is not absolute".format(part.mountpoint)
                    )
            if part.role == "swap" and part.mountpoint:
                issues.append("swap partitions have no mount point")
            if part.role not in ("esp", "swap", "root", "data"):
                issues.append("unknown partition role {}".format(part.role))
            if part.role != "swap" and not part.fstype:
                issues.append(
                    "partition {} has no filesystem".format(part.number)
                )
    if layout.find_mount("/") is None:
        issues.append("no partition is mounted at /")
    if layout.find_mount("/boot") is None:
        issues.append("no partition is mounted at /boot")
    for part in layout.data:
        if not part.mountpoint or part.mountpoint == "/":
            issues.append("data partitions need a mount point")
        elif part.mountpoint.startswith("/boot/"):
            issues.append(
                "data partition mount points below /boot are not supported"
            )
    return issues


def _unit_for(layout: InstallLayout, part: disk.PlannedPartition) -> int:
    item = layout.disk_for(part)
    return item.unit if item is not None else 512


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def _safe_name(disk_path: str) -> str:
    name = os.path.basename(disk_path) or "disk"
    return re.sub(r"[^A-Za-z0-9_.-]", "_", name)


def backup_paths(
    item: DiskLayout, backup_dir: str = "/run/browneye/backup"
) -> tuple[str, str]:
    name = _safe_name(item.disk_path)
    return (
        os.path.join(backup_dir, name + ".sfdisk"),
        os.path.join(backup_dir, name),
    )


def snapshot_commands(
    item: DiskLayout, backup_dir: str = "/run/browneye/backup"
) -> list[Command]:
    dump_path, prefix = backup_paths(item, backup_dir)
    blank = item.table.is_blank
    return [
        Command(
            argv=("mkdir", "-p", backup_dir),
            step="partition",
            description="create partition-table backup directory",
        ),
        Command(
            argv=("sfdisk", "--dump", item.disk_path),
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
                item.disk_path,
            ),
            step="partition",
            description="save the binary primary/backup GPT sectors",
            allow_failure=blank,
        ),
    ]


def delete_commands(item: DiskLayout) -> list[Command]:
    commands: list[Command] = []
    for number in item.delete_numbers:
        part = item.table.find_number(number)
        node = (part.node if part else "") or disk._node_for(item.disk_path, number)
        commands.append(
            Command(
                argv=("wipefs", "--all", "--force", node),
                step="partition",
                description="clear filesystem signatures on partition {}".format(
                    number
                ),
            )
        )
        commands.append(
            Command(
                argv=(
                    "sfdisk",
                    "--delete",
                    "--no-reread",
                    item.disk_path,
                    str(number),
                ),
                step="partition",
                description="delete partition {}".format(number),
            )
        )
    return commands


def reread_commands(item: DiskLayout, step: str = "partition") -> list[Command]:
    return [
        Command(
            argv=("blockdev", "--rereadpt", item.disk_path),
            step=step,
            description="ask the kernel to reread the partition table",
            allow_failure=True,
        ),
        Command(
            argv=("partx", "-u", item.disk_path),
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


def write_table_commands(item: DiskLayout) -> list[Command]:
    if not item.new_table_text:
        return []
    return [
        Command(
            argv=(
                "sfdisk",
                "--no-reread",
                "--lock=yes",
                item.disk_path,
            ),
            step="partition",
            description="write the complete replacement GPT preserving other entries",
            stdin=item.new_table_text,
            stdin_redacted=False,
        ),
        *reread_commands(item),
        Command(
            argv=("sfdisk", "--verify", item.disk_path),
            step="partition",
            description="verify the written GPT",
        ),
    ]


def partition_commands(
    item: DiskLayout, backup_dir: str = "/run/browneye/backup"
) -> list[Command]:
    if not item.changed:
        return []
    return (
        snapshot_commands(item, backup_dir)
        + delete_commands(item)
        + write_table_commands(item)
    )


def rollback_commands(
    item: DiskLayout, backup_dir: str = "/run/browneye/backup"
) -> list[Command]:
    dump_path, _prefix = backup_paths(item, backup_dir)
    return [
        Command(
            argv=("sfdisk", "--no-reread", item.disk_path),
            step="partition",
            description="restore the saved partition table after a verification failure",
            stdin_path=dump_path,
            stdin_redacted=False,
        ),
        *reread_commands(item),
        Command(
            argv=("sfdisk", "--verify", item.disk_path),
            step="partition",
            description="verify the restored GPT",
        ),
    ]


def verify_preserved(
    item: DiskLayout, after: disk.PartitionTable
) -> list[str]:
    return disk.verify_preserved(
        item.table,
        after,
        item.delete_numbers,
        tuple(part.number for part in item.new_partitions),
    )


def verify_planned(item: DiskLayout, after: disk.PartitionTable) -> list[str]:
    issues: list[str] = []
    after_by_number = after.by_number()
    for part in item.new_partitions:
        other = after_by_number.get(part.number)
        if other is None:
            issues.append(
                "planned partition {} ({}) is missing".format(
                    part.number, part.role
                )
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
                        "planned partition {} ({}) {} changed: {} -> {}".format(
                            part.number, part.role, label, old, new
                        )
                    )
            elif old != new:
                issues.append(
                    "planned partition {} ({}) {} changed: {!r} -> {!r}".format(
                        part.number, part.role, label, old, new
                    )
                )
    return issues


def _format_label(part: disk.PlannedPartition) -> str:
    if part.label:
        return part.label
    return _label_for(part.role, part.mountpoint, part.fstype or "")


def _partition_to_format(part: disk.PlannedPartition) -> bool:
    if not part.fstype or part.role == "swap" and part.fstype != "swap":
        return False
    if part.existing and not part.format:
        return False
    return True


def _mkfs_command(item: DiskLayout, part: disk.PlannedPartition) -> Command | None:
    device = part.by_partuuid
    fstype = (part.fstype or "").lower()
    label = _format_label(part)
    if part.role == "esp" or fstype == "vfat":
        argv = ["mkfs.fat", "-F", "32", "-n", label[:_FAT_LABEL_MAX]]
        if item.unit == 4096:
            argv.extend(["-S", "4096"])
        if part.fs_uuid:
            argv.extend(["-i", part.fs_uuid.replace("-", "")[:8].upper()])
        argv.append(device)
        return Command(
            argv=tuple(argv),
            step="format",
            description="create the FAT32 filesystem on partition {}".format(
                part.number
            ),
        )
    if fstype == "swap" or part.role == "swap":
        argv = ["mkswap", "-L", label]
        if part.fs_uuid:
            argv.extend(["-U", part.fs_uuid])
        argv.append(device)
        return Command(
            argv=tuple(argv),
            step="format",
            description="create the swap area on partition {}".format(part.number),
        )
    if fstype == "btrfs":
        argv = ["mkfs.btrfs", "-f", "-L", label]
        if part.fs_uuid:
            argv.extend(["-U", part.fs_uuid])
        argv.append(device)
        return Command(
            argv=tuple(argv),
            step="format",
            description="create the btrfs filesystem on partition {}".format(
                part.number
            ),
        )
    if fstype == "ext4":
        argv = [
            "mke2fs",
            "-t",
            "ext4",
            "-F",
            "-L",
            label[:_LABEL_MAX],
            "-m",
            "1",
        ]
        if part.fs_uuid:
            argv.extend(["-U", part.fs_uuid])
        argv.extend(
            [
                "-E",
                "lazy_itable_init=0,lazy_journal_init=0,nodiscard",
                device,
            ]
        )
        return Command(
            argv=tuple(argv),
            step="format",
            description="create the ext4 filesystem on partition {}".format(
                part.number
            ),
        )
    return None


def format_commands(item: DiskLayout) -> list[Command]:
    commands: list[Command] = []
    for part in item.partitions:
        if _partition_to_format(part):
            command = _mkfs_command(item, part)
            if command is not None:
                commands.append(command)
    return commands


@dataclass(frozen=True)
class FormatCheck:
    part: disk.PlannedPartition
    expected_fstype: str
    type_command: Command
    uuid_command: Command


_EXPECTED_FSTYPE = {
    "ext4": "ext4",
    "btrfs": "btrfs",
    "vfat": "vfat",
    "swap": "swap",
}


def format_checks(item: DiskLayout) -> tuple[FormatCheck, ...]:
    checks: list[FormatCheck] = []
    for part in item.partitions:
        if not _partition_to_format(part):
            continue
        expected = _EXPECTED_FSTYPE.get((part.fstype or "").lower())
        if expected is None:
            continue
        checks.append(
            FormatCheck(
                part=part,
                expected_fstype=expected,
                type_command=Command(
                    argv=(
                        "blkid",
                        "-p",
                        "-s",
                        "TYPE",
                        "-o",
                        "value",
                        part.by_partuuid,
                    ),
                    step="format",
                    description="verify the filesystem type on partition {}".format(
                        part.number
                    ),
                    read_only=True,
                    destructive=False,
                ),
                uuid_command=Command(
                    argv=(
                        "blkid",
                        "-p",
                        "-s",
                        "UUID",
                        "-o",
                        "value",
                        part.by_partuuid,
                    ),
                    step="format",
                    description="verify the filesystem UUID on partition {}".format(
                        part.number
                    ),
                    read_only=True,
                    destructive=False,
                ),
            )
        )
    return tuple(checks)


def all_format_commands(layout: InstallLayout) -> list[Command]:
    return [command for item in layout.disks for command in format_commands(item)]


def all_format_checks(layout: InstallLayout) -> tuple[FormatCheck, ...]:
    return tuple(check for item in layout.disks for check in format_checks(item))


def all_partition_commands(
    layout: InstallLayout, backup_dir: str = "/run/browneye/backup"
) -> list[Command]:
    return [
        command
        for item in layout.disks
        for command in partition_commands(item, backup_dir)
    ]


def all_rollback_commands(
    layout: InstallLayout, backup_dir: str = "/run/browneye/backup"
) -> list[Command]:
    return [
        command
        for item in layout.disks
        if item.changed
        for command in rollback_commands(item, backup_dir)
    ]


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def partition_size_mib(item: DiskLayout, part: disk.PlannedPartition) -> int:
    return (part.size * item.unit) // MIB


def mount_sort_key(part: disk.PlannedPartition) -> tuple[int, str]:
    """Parents before children, so nested mount points are created in order."""

    mountpoint = part.mountpoint or "/"
    return (mountpoint.count("/"), mountpoint)


def describe_layout(layout: InstallLayout) -> list[str]:
    lines: list[str] = []
    for item in layout.disks:
        lines.append(
            "{}  {}".format(item.disk_path, disk.human_size(
                (item.total_sectors or 0) * item.unit
            ))
        )
        for part in item.partitions:
            lines.append(
                "  {} {}  {}  {}{}".format(
                    ">",
                    part.number,
                    disk.human_size(part.size * item.unit),
                    part.fstype,
                    "  " + part.mountpoint if part.mountpoint else "",
                )
            )
    return lines
