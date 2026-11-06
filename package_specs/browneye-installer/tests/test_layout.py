"""Unit tests for the multi-disk layout planner."""

from __future__ import annotations

import dataclasses
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "files"))

import disk  # noqa: E402
import layout  # noqa: E402
from disk import (  # noqa: E402
    ESP_TYPE,
    LINUX_FS_TYPE,
    LINUX_SWAP_TYPE,
    PartitionTable,
    PlanError,
)

FIXTURES = HERE / "fixtures"
MIB = 1024 * 1024


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def blank_table(path: str = "/dev/vda", total_sectors: int = 41943040, unit: int = 512):
    total_bytes = total_sectors * unit
    first = max(1, MIB // unit)
    return PartitionTable(
        device=path,
        label="gpt",
        id="99999999-8888-7777-6666-555555555555",
        unit=unit,
        firstlba=first,
        lastlba=total_sectors - 34,
        total_sectors=total_bytes // unit,
    )


def windows_table(**kwargs):
    return disk.parse_sfdisk_json(
        fixture("sfdisk-gpt-windows.json"),
        device="/dev/vda",
        total_sectors=41943040,
        **kwargs,
    )


def root_specs(root_fstype: str = "ext4"):
    return (
        layout.PartitionSpec("esp", "vfat", "/boot", size_mib=1024),
        layout.PartitionSpec("swap", "swap", None, size_mib=2048),
        layout.PartitionSpec("root", root_fstype, "/"),
    )


class PlanDiskTest(unittest.TestCase):
    def test_blank_disk_default(self):
        table = blank_table()
        spec = layout.DiskSpec(path="/dev/vda", partitions=root_specs())
        plan = layout.plan_disk(table, spec, disk_path="/dev/vda")
        self.assertEqual(
            [(part.role, part.number) for part in plan.partitions],
            [("esp", 1), ("swap", 2), ("root", 3)],
        )
        self.assertEqual(plan.esp.type, ESP_TYPE)
        self.assertEqual(plan.swap.type, LINUX_SWAP_TYPE)
        self.assertEqual(plan.root.type, LINUX_FS_TYPE)
        self.assertEqual(
            (plan.root.size * plan.unit) // MIB,
            20478 - 1024 - 2048,
        )
        self.assertEqual(disk.render_new_table(
            disk_path=plan.disk_path,
            disk_id=plan.disk_id,
            first_lba=plan.first_lba,
            last_lba=plan.last_lba,
            unit=plan.unit,
            remaining=table.without(plan.delete_numbers),
            new_parts=plan.new_partitions,
            delete_numbers=plan.delete_numbers,
        ), plan.new_table_text)

    def test_btrfs_root_and_home_on_second_disk(self):
        tables = {
            "/dev/vda": blank_table("/dev/vda"),
            "/dev/vdb": blank_table("/dev/vdb"),
        }
        spec = layout.InstallSpec(
            disks=(
                layout.DiskSpec(
                    path="/dev/vda",
                    partitions=root_specs("btrfs"),
                ),
                layout.DiskSpec(
                    path="/dev/vdb",
                    partitions=(
                        layout.PartitionSpec("data", "ext4", "/home"),
                    ),
                ),
            )
        )
        plan = layout.plan_install(tables, spec)
        self.assertEqual(layout.validate_layout(plan), [])
        self.assertEqual(plan.root.fstype, "btrfs")
        self.assertEqual(plan.find_mount("/home").fstype, "ext4")
        commands = [command.argv for command in layout.all_format_commands(plan)]
        self.assertTrue(any(argv[0] == "mkfs.btrfs" for argv in commands))
        self.assertTrue(any(argv[0] == "mke2fs" for argv in commands))
        self.assertTrue(any(argv[0] == "mkfs.fat" for argv in commands))
        self.assertTrue(any(argv[0] == "mkswap" for argv in commands))

    def test_explicit_sizes_leave_a_warning(self):
        table = blank_table()
        spec = layout.DiskSpec(
            path="/dev/vda",
            partitions=(
                layout.PartitionSpec("esp", "vfat", "/boot", size_mib=512),
                layout.PartitionSpec("root", "ext4", "/", size_mib=8192),
            ),
        )
        plan = layout.plan_disk(table, spec, disk_path="/dev/vda")
        self.assertEqual((plan.root.size * plan.unit) // MIB, 8192)
        self.assertTrue(
            any("unallocated" in warning for warning in plan.warnings)
        )

    def test_root_below_minimum_is_refused(self):
        table = blank_table()
        spec = layout.DiskSpec(
            path="/dev/vda",
            partitions=(
                layout.PartitionSpec("esp", "vfat", "/boot", size_mib=1024),
                layout.PartitionSpec("root", "ext4", "/", size_mib=4096),
            ),
        )
        with self.assertRaises(PlanError):
            layout.plan_disk(table, spec, disk_path="/dev/vda")

    def test_region_too_small_is_refused(self):
        total = 8 * 1024 * 1024 * 1024 // 512
        table = blank_table(total_sectors=total)
        spec = layout.DiskSpec(path="/dev/vda", partitions=root_specs())
        with self.assertRaises(PlanError):
            layout.plan_disk(table, spec, disk_path="/dev/vda")

    def test_mbr_is_refused(self):
        table = disk.parse_sfdisk_json(
            fixture("sfdisk-dos.json"), device="/dev/vdc", total_sectors=41943040
        )
        spec = layout.DiskSpec(path="/dev/vdc", partitions=root_specs())
        with self.assertRaises(PlanError):
            layout.plan_disk(table, spec, disk_path="/dev/vdc")

    def test_4kn_sizes_and_fat_flag(self):
        total = 5242880
        table = blank_table("/dev/vdd", total_sectors=total, unit=4096)
        spec = layout.DiskSpec(path="/dev/vdd", partitions=root_specs())
        plan = layout.plan_disk(table, spec, disk_path="/dev/vdd")
        self.assertEqual((plan.esp.size * plan.unit) // MIB, 1024)
        self.assertEqual(plan.root.start % 256, 0)
        esp = next(
            command
            for command in layout.format_commands(plan)
            if command.argv[0] == "mkfs.fat"
        )
        self.assertIn("-S", esp.argv)
        self.assertIn("4096", esp.argv)

    def test_existing_esp_is_reused(self):
        table = windows_table()
        spec = layout.DiskSpec(
            path="/dev/vda",
            partitions=(
                layout.PartitionSpec(
                    "esp",
                    "vfat",
                    "/boot",
                    existing_number=1,
                    format=False,
                ),
                layout.PartitionSpec("root", "ext4", "/"),
            ),
        )
        plan = layout.plan_disk(table, spec, disk_path="/dev/vda")
        self.assertTrue(plan.esp.existing)
        self.assertEqual(plan.esp.number, 1)
        self.assertEqual(plan.esp.partuuid, "AAAAAAAA-1111-2222-3333-444444444444")
        commands = [command.argv for command in layout.format_commands(plan)]
        self.assertFalse(any(argv[0] == "mkfs.fat" for argv in commands))
        self.assertIn("uuid=AAAAAAAA-1111-2222-3333-444444444444", plan.new_table_text)

    def test_adopted_existing_partition_is_not_formatted(self):
        table = windows_table()
        home_part = dataclasses.replace(
            table.partitions[1],
            fstype="ext4",
            fs_uuid="22222222-3333-4444-5555-666666666666",
        )
        table = dataclasses.replace(
            table,
            partitions=(table.partitions[0], home_part, table.partitions[2]),
        )
        spec = layout.DiskSpec(
            path="/dev/vda",
            partitions=(
                layout.PartitionSpec(
                    "esp",
                    "vfat",
                    "/boot",
                    existing_number=1,
                    format=False,
                ),
                layout.PartitionSpec(
                    "data",
                    "ext4",
                    "/home",
                    existing_number=2,
                    format=False,
                ),
                layout.PartitionSpec("root", "ext4", "/"),
            ),
        )
        plan = layout.plan_disk(table, spec, disk_path="/dev/vda")
        home = plan.data[0]
        self.assertTrue(home.existing)
        self.assertEqual(home.number, 2)
        formatted = [
            command.argv for command in layout.format_commands(plan)
        ]
        self.assertFalse(
            any(
                str(home.by_partuuid) in argv for argv in formatted
            )
        )

    def test_adopted_existing_partition_can_be_reformatted(self):
        table = windows_table()
        spec = layout.DiskSpec(
            path="/dev/vda",
            partitions=(
                layout.PartitionSpec(
                    "esp",
                    "vfat",
                    "/boot",
                    existing_number=1,
                    format=False,
                ),
                layout.PartitionSpec(
                    "data",
                    "ext4",
                    "/home",
                    existing_number=2,
                    format=True,
                ),
                layout.PartitionSpec("root", "ext4", "/"),
            ),
        )
        plan = layout.plan_disk(table, spec, disk_path="/dev/vda")
        home = plan.data[0]
        self.assertTrue(home.format)
        formatted = [
            command.argv for command in layout.format_commands(plan)
        ]
        self.assertTrue(
            any(
                argv[0] == "mke2fs" and str(home.by_partuuid) in argv
                for argv in formatted
            )
        )

    def test_deleted_partition_number_can_be_reused(self):
        table = windows_table()
        spec = layout.DiskSpec(
            path="/dev/vda",
            delete_partitions=(2,),
            partitions=(
                layout.PartitionSpec(
                    "esp",
                    "vfat",
                    "/boot",
                    existing_number=1,
                    format=False,
                ),
                layout.PartitionSpec("swap", "swap", None, size_mib=2048),
                layout.PartitionSpec("root", "ext4", "/"),
            ),
        )
        plan = layout.plan_disk(table, spec, disk_path="/dev/vda")
        self.assertEqual(plan.swap.number, 2)
        self.assertNotIn(
            "BBBBBBBB-1111-2222-3333-444444444444", plan.new_table_text
        )
        self.assertIn(
            "AAAAAAAA-1111-2222-3333-444444444444", plan.new_table_text
        )
        self.assertIn(
            "CCCCCCCC-1111-2222-3333-444444444444", plan.new_table_text
        )


class SpecMappingTest(unittest.TestCase):
    def test_parse_multi_disk_layout(self):
        spec = layout.InstallSpec.from_mapping(
            {
                "disks": [
                    {
                        "path": "/dev/vda",
                        "delete_partitions": [2],
                        "partitions": [
                            {
                                "role": "esp",
                                "fstype": "vfat",
                                "mountpoint": "/boot",
                                "existing_number": 1,
                                "format": False,
                            },
                            {
                                "role": "root",
                                "fstype": "btrfs",
                                "mountpoint": "/",
                            },
                        ],
                    },
                    {
                        "path": "/dev/vdb",
                        "partitions": [
                            {
                                "role": "data",
                                "fstype": "ext4",
                                "mountpoint": "/home",
                                "size_mib": 10240,
                            }
                        ],
                    },
                ]
            }
        )
        self.assertEqual(len(spec.disks), 2)
        self.assertEqual(spec.disks[0].delete_partitions, (2,))
        self.assertEqual(spec.disks[0].partitions[0].existing_number, 1)
        self.assertFalse(spec.disks[0].partitions[0].format)
        self.assertEqual(spec.disks[1].partitions[0].mountpoint, "/home")
        self.assertEqual(spec.disks[1].partitions[0].size_mib, 10240)

    def test_adopted_partition_defaults_to_no_format(self):
        spec = layout.InstallSpec.from_mapping(
            {
                "disks": [
                    {
                        "path": "/dev/vda",
                        "partitions": [
                            {
                                "role": "data",
                                "fstype": "ext4",
                                "mountpoint": "/home",
                                "existing_number": 3,
                            }
                        ],
                    }
                ]
            }
        )
        self.assertFalse(spec.disks[0].partitions[0].format)

    def test_unknown_partition_key_is_rejected(self):
        with self.assertRaises(ValueError):
            layout.InstallSpec.from_mapping(
                {
                    "disks": [
                        {
                            "path": "/dev/vda",
                            "partitions": [
                                {
                                    "role": "root",
                                    "fstype": "ext4",
                                    "mountpoint": "/",
                                    "typo": True,
                                }
                            ],
                        }
                    ]
                }
            )

    def test_invalid_partition_is_rejected(self):
        with self.assertRaises(ValueError):
            layout.InstallSpec.from_mapping(
                {
                    "disks": [
                        {
                            "path": "/dev/vda",
                            "partitions": [
                                {
                                    "role": "root",
                                    "fstype": "vfat",
                                    "mountpoint": "/",
                                }
                            ],
                        }
                    ]
                }
            )


class GuidedLayoutTest(unittest.TestCase):
    def test_erase_disk_deletes_every_existing_entry(self):
        table = windows_table()
        spec = layout.plan_erase_disk(table, fstype="ext4", swap="none")
        self.assertEqual(spec.delete_partitions, (1, 2, 3))
        self.assertEqual(
            [(part.role, part.mountpoint) for part in spec.partitions],
            [("esp", "/boot"), ("root", "/")],
        )
        plan = layout.plan_disk(table, spec, disk_path="/dev/vda")
        self.assertEqual(layout.validate_layout(
            layout.InstallLayout((plan,))
        ), [])
        self.assertFalse(plan.esp.existing)
        self.assertEqual(plan.esp.number, 1)
        self.assertEqual(plan.root.number, 2)
        self.assertGreater(
            (plan.root.size * plan.unit) // MIB, 15 * 1024
        )

    def test_erase_disk_can_keep_a_swap_partition(self):
        table = blank_table()
        spec = layout.plan_erase_disk(table, fstype="btrfs", swap="partition")
        self.assertEqual(
            [part.role for part in spec.partitions],
            ["esp", "swap", "root"],
        )
        plan = layout.plan_disk(table, spec, disk_path="/dev/vda")
        self.assertEqual(plan.root.fstype, "btrfs")
        self.assertEqual((plan.swap.size * plan.unit) // MIB, 2048)

    def test_free_space_reuses_the_existing_esp_and_keeps_data(self):
        table = windows_table()
        spec = layout.plan_free_space(table, fstype="ext4", swap="none")
        self.assertEqual(spec.delete_partitions, ())
        self.assertEqual(
            [part.role for part in spec.partitions], ["esp", "root"]
        )
        self.assertEqual(spec.partitions[0].existing_number, 1)
        self.assertFalse(spec.partitions[0].format)
        plan = layout.plan_disk(table, spec, disk_path="/dev/vda")
        self.assertTrue(plan.esp.existing)
        self.assertFalse(plan.root.existing)
        self.assertGreaterEqual(plan.root.start, table.partitions[-1].end)
        self.assertEqual(layout.validate_layout(
            layout.InstallLayout((plan,))
        ), [])
        self.assertEqual(plan.delete_numbers, ())
        self.assertEqual(
            {part.number for part in plan.table.partitions}, {1, 2, 3}
        )

    def test_free_space_on_a_blank_disk_creates_an_esp(self):
        table = blank_table()
        spec = layout.plan_free_space(table, fstype="ext4", swap="none")
        self.assertEqual(
            [part.role for part in spec.partitions], ["esp", "root"]
        )
        self.assertIsNone(spec.partitions[0].existing_number)
        plan = layout.plan_disk(table, spec, disk_path="/dev/vda")
        self.assertEqual(layout.validate_layout(
            layout.InstallLayout((plan,))
        ), [])

    def test_free_space_without_enough_room_is_refused(self):
        table = windows_table()
        last = table.partitions[-1]
        filled = dataclasses.replace(last, size=table.lastlba - last.start)
        table = dataclasses.replace(
            table,
            partitions=(table.partitions[0], table.partitions[1], filled),
        )
        with self.assertRaises(PlanError):
            layout.plan_free_space(table, fstype="ext4", swap="none")


class ValidateLayoutTest(unittest.TestCase):
    def _plan(self):
        table = blank_table()
        spec = layout.DiskSpec(path="/dev/vda", partitions=root_specs())
        return layout.plan_disk(table, spec, disk_path="/dev/vda")

    def test_clean_plan(self):
        self.assertEqual(layout.validate_layout(layout.InstallLayout((self._plan(),))), [])

    def test_duplicate_mount_point_is_detected(self):
        spec = layout.InstallSpec(
            disks=(
                layout.DiskSpec(
                    path="/dev/vda",
                    partitions=(
                        layout.PartitionSpec("esp", "vfat", "/boot", size_mib=1024),
                        layout.PartitionSpec("root", "ext4", "/"),
                    ),
                ),
                layout.DiskSpec(
                    path="/dev/vdb",
                    partitions=(
                        layout.PartitionSpec("root", "ext4", "/"),
                    ),
                ),
            )
        )
        issues = spec.validate()
        self.assertTrue(any("assigned twice" in issue for issue in issues))
        self.assertTrue(any("exactly one root" in issue for issue in issues))

    def test_missing_esp_is_detected(self):
        spec = layout.InstallSpec(
            disks=(
                layout.DiskSpec(
                    path="/dev/vda",
                    partitions=(
                        layout.PartitionSpec("root", "ext4", "/"),
                    ),
                ),
            )
        )
        self.assertTrue(
            any("EFI System Partition" in issue for issue in spec.validate())
        )

    def test_format_checks_map_filesystems(self):
        plan = self._plan()
        checks = layout.all_format_checks(layout.InstallLayout((plan,)))
        self.assertEqual(
            {check.expected_fstype for check in checks},
            {"vfat", "swap", "ext4"},
        )

    def test_plan_dict_is_serialisable(self):
        import json

        payload = layout.InstallLayout((self._plan(),)).to_dict()
        text = json.dumps(payload, sort_keys=True)
        self.assertIn('"mountpoint": "/boot"', text)
        self.assertEqual(payload["disks"][0]["disk"], "/dev/vda")


class BuildLayoutTest(unittest.TestCase):
    def test_main_build_layout_probes_each_disk(self):
        from install import InstallConfig
        from main import build_layout
        from probe import ProbedDisk

        tables = {
            "/dev/vda": blank_table("/dev/vda"),
            "/dev/vdb": blank_table("/dev/vdb"),
        }

        class FakeProbe:
            def __init__(self):
                self.disks = {
                    path: ProbedDisk(
                        disk=disk.Disk(
                            path=path,
                            kname=path.rsplit("/", 1)[-1],
                            size_bytes=table.total_sectors * table.unit,
                            sector_size=table.unit,
                        ),
                        table=table,
                        selectable=True,
                    )
                    for path, table in tables.items()
                }

            def find_disk(self, path, refresh=False):
                return self.disks.get(path)

            def read_table(self, probed):
                return tables[probed.disk.path]

        spec = layout.InstallSpec(
            disks=(
                layout.DiskSpec(
                    path="/dev/vda",
                    partitions=root_specs("ext4"),
                ),
                layout.DiskSpec(
                    path="/dev/vdb",
                    partitions=(
                        layout.PartitionSpec("data", "btrfs", "/home"),
                    ),
                ),
            )
        )
        config = InstallConfig(
            layout=spec,
            admin_password="test-password",
            confirm_disk="/dev/vda",
            confirm_phrase="ERASE",
        )
        self.assertEqual(config.validate(), [])
        plan, probed, regions = build_layout(FakeProbe(), config)
        self.assertEqual(len(probed), 2)
        self.assertEqual(set(regions), {"/dev/vda", "/dev/vdb"})
        self.assertEqual(plan.root.role, "root")
        self.assertEqual(plan.find_mount("/home").fstype, "btrfs")


if __name__ == "__main__":
    unittest.main()
