"""Unit tests for the pure disk planner.

Run from the repository root (no root, no block devices touched):

    python3 -m unittest discover -s package_specs/browneye-installer/tests -v
"""

from __future__ import annotations

import dataclasses
import json
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "files"))

import disk  # noqa: E402
from disk import (  # noqa: E402
    ESP_TYPE,
    LINUX_FS_TYPE,
    LINUX_SWAP_TYPE,
    PartitionTable,
    PlanError,
    align_down,
    align_up,
)

FIXTURES = HERE / "fixtures"
MIB = 1024 * 1024
GIB = 1024 * MIB


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def windows_table(**kwargs) -> PartitionTable:
    return disk.parse_sfdisk_json(
        fixture("sfdisk-gpt-windows.json"),
        device="/dev/vda",
        total_sectors=41943040,
        **kwargs,
    )


def blank_table(total_sectors: int = 41943040, unit: int = 512) -> PartitionTable:
    total_bytes = total_sectors * unit
    total_table = total_bytes // unit
    first = max(1, MIB // unit)
    last = total_table - 34
    return PartitionTable(
        device="/dev/vda",
        label="gpt",
        id="99999999-8888-7777-6666-555555555555",
        unit=unit,
        firstlba=first,
        lastlba=last,
        total_sectors=total_table,
    )


class ParseSfdiskTest(unittest.TestCase):
    def test_gpt_windows(self):
        table = windows_table()
        self.assertEqual(table.label, "gpt")
        self.assertEqual(table.unit, 512)
        self.assertEqual(table.id, "11111111-2222-3333-4444-555555555555")
        self.assertEqual(table.firstlba, 2048)
        self.assertEqual(table.lastlba, 41943006)
        self.assertEqual(len(table.partitions), 3)
        first = table.partitions[0]
        self.assertEqual(first.number, 1)
        self.assertEqual(first.start, 2048)
        self.assertEqual(first.size, 1048576)
        self.assertEqual(first.type, ESP_TYPE)
        self.assertEqual(first.partuuid, "AAAAAAAA-1111-2222-3333-444444444444")
        self.assertEqual(first.fs_uuid, "1234-ABCD")
        self.assertEqual(first.name, "EFI")
        self.assertEqual(table.partitions[2].attrs, "RequiredPartition")

    def test_empty_and_invalid_are_blank(self):
        for raw in ("", "not json", "{}", None):
            table = disk.parse_sfdisk_json(
                raw, device="/dev/vda", total_sectors=1000
            )
            self.assertTrue(table.is_blank)
            self.assertEqual(table.device, "/dev/vda")
            self.assertEqual(table.total_sectors, 1000)
            self.assertEqual(table.partitions, ())

    def test_mbr_and_extended(self):
        table = disk.parse_sfdisk_json(
            fixture("sfdisk-dos.json"), device="/dev/vdc", total_sectors=41943040
        )
        self.assertTrue(table.is_mbr)
        self.assertFalse(table.has_extended())
        extended = dataclasses.replace(
            table,
            partitions=table.partitions
            + (disk.Partition(node="/dev/vdc3", number=3, start=2103296, size=100, type="05"),),
        )
        self.assertTrue(extended.has_extended())

    def test_4kn_unit(self):
        table = disk.parse_sfdisk_json(
            fixture("sfdisk-4kn.json"), device="/dev/vdd", total_sectors=5242880
        )
        self.assertEqual(table.unit, 4096)
        self.assertEqual(table.partitions[0].size, 131072)


class ParseLsblkTest(unittest.TestCase):
    def test_disks_children_and_ignored_loop(self):
        disks = disk.parse_lsblk_json(fixture("lsblk.json"))
        self.assertEqual([d.kname for d in disks], ["vda", "sdb", "vdb"])
        vda = disks[0]
        self.assertEqual(vda.model, "QEMU HARDDISK")
        self.assertEqual(vda.serial, "QM00001")
        self.assertEqual(len(vda.children), 1)
        self.assertEqual(vda.children[0].number, 1)
        self.assertEqual(vda.children[0].fs_uuid, "1234-ABCD")
        self.assertEqual(vda.children[0].fstype, "vfat")
        sdb = disks[1]
        self.assertEqual(sdb.mountpoints, ("/run/initramfs/live",))
        vdb = disks[2]
        self.assertEqual(vdb.mountpoints, ("/mnt/data",))


class AlignmentTest(unittest.TestCase):
    def test_align(self):
        self.assertEqual(align_up(2049, 2048), 4096)
        self.assertEqual(align_up(2048, 2048), 2048)
        self.assertEqual(align_down(4095, 2048), 2048)
        self.assertEqual(align_down(4096, 2048), 4096)
        self.assertEqual(align_up(257, 256), 512)


class FreeRegionTest(unittest.TestCase):
    def test_tail_gap_stops_before_backup_gpt(self):
        table = windows_table()
        regions = disk.find_free_regions(table, 41943040)
        self.assertEqual(len(regions), 1)
        region = regions[0]
        self.assertEqual(region.start, 17860608)
        self.assertEqual(region.end, 41940992)
        self.assertEqual(region.size, 24080384)
        self.assertEqual((region.start_mib, region.end_mib), (8721, 20479))
        self.assertEqual(region.size_mib, 11758)
        # Never include the backup GPT at the end of the device.
        self.assertLess(region.end, 41943040 - 33)

    def test_gap_between_partitions_and_tail(self):
        table = disk.parse_sfdisk_json(
            fixture("sfdisk-gpt-gap.json"), device="/dev/vdb", total_sectors=2097152
        )
        regions = disk.find_free_regions(table, 2097152)
        self.assertEqual(len(regions), 2)
        middle, tail = regions
        self.assertEqual((middle.start, middle.end), (22528, 100352))
        self.assertEqual(middle.size_mib, 38)
        self.assertEqual((tail.start_mib, tail.end_mib, tail.size_mib), (59, 1023, 964))
        self.assertGreater(tail.size, middle.size)

    def test_blank_gpt(self):
        table = disk.parse_sfdisk_json(
            fixture("sfdisk-gpt-blank.json"), device="/dev/vda", total_sectors=41943040
        )
        regions = disk.find_free_regions(table, 41943040)
        self.assertEqual(len(regions), 1)
        self.assertEqual(regions[0].start, 2048)
        self.assertEqual(regions[0].end, 41940992)
        self.assertEqual(regions[0].size_mib, 20478)

    def test_mbr_uses_full_device_end(self):
        table = disk.parse_sfdisk_json(
            fixture("sfdisk-dos.json"), device="/dev/vdc", total_sectors=41943040
        )
        regions = disk.find_free_regions(table, 41943040)
        self.assertEqual(len(regions), 1)
        self.assertEqual(regions[0].start, 2103296)
        self.assertEqual(regions[0].end, 41943040)
        self.assertEqual(regions[0].size_mib, 19453)

    def test_4kn_alignment_and_units(self):
        table = disk.parse_sfdisk_json(
            fixture("sfdisk-4kn.json"), device="/dev/vdd", total_sectors=5242880
        )
        regions = disk.find_free_regions(table, 5242880)
        self.assertEqual(len(regions), 1)
        region = regions[0]
        self.assertEqual(region.unit, 4096)
        self.assertEqual(region.start % 256, 0)
        self.assertEqual(region.end % 256, 0)
        self.assertEqual(region.end, 5242624)
        # 512 MiB is 131072 sectors on 4Kn, not 1048576.
        self.assertEqual((512 * MIB) // 4096, 131072)

    def test_small_gaps_are_dropped(self):
        table = PartitionTable(
            device="/dev/vda",
            label="gpt",
            id="id",
            unit=512,
            firstlba=2048,
            lastlba=41943006,
            total_sectors=41943040,
            partitions=(
                disk.Partition(node="/dev/vda1", number=1, start=2048, size=2048),
                # gap of 1024 sectors (0.5 MiB) before p2
                disk.Partition(node="/dev/vda2", number=2, start=5120, size=2048),
            ),
        )
        regions = disk.find_free_regions(table, 41943040, min_mib=2)
        self.assertEqual(len(regions), 1)  # only the tail remains
        self.assertGreater(regions[0].start, 7168)

    def test_choose_largest_usable_region(self):
        table = disk.parse_sfdisk_json(
            fixture("sfdisk-gpt-gap.json"), device="/dev/vdb", total_sectors=2097152
        )
        regions = disk.find_free_regions(table, 2097152)
        chosen = disk.choose_region(regions, required_mib=100)
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen.start_mib, 59)
        self.assertIsNone(disk.choose_region(regions, required_mib=10000))
        by_start = disk.choose_region(regions, start_mib=11)
        self.assertEqual(by_start.start_mib, 11)


class PlanTest(unittest.TestCase):
    def test_reuses_existing_esp_and_fills_region(self):
        table = windows_table()
        region = disk.find_free_regions(table, 41943040)[0]
        plan = disk.plan_layout(
            table, region, disk_path="/dev/vda", total_sectors=41943040
        )
        self.assertTrue(plan.esp.existing)
        self.assertEqual(plan.esp.number, 1)
        self.assertEqual(plan.esp.partuuid, "AAAAAAAA-1111-2222-3333-444444444444")
        self.assertEqual(plan.esp.fs_uuid, "1234-ABCD")
        self.assertIsNotNone(plan.swap)
        self.assertEqual((plan.swap.size * plan.unit) // MIB, 2048)
        self.assertEqual((plan.root.size * plan.unit) // MIB, 9710)
        self.assertGreaterEqual((plan.root.size * plan.unit) // MIB, 8192)
        self.assertEqual(plan.root.type, LINUX_FS_TYPE)
        self.assertEqual(plan.swap.type, LINUX_SWAP_TYPE)
        self.assertEqual(disk.validate_plan(plan), [])
        # Existing partitions are preserved verbatim.
        text = plan.new_table_text
        self.assertIn("uuid=AAAAAAAA-1111-2222-3333-444444444444", text)
        self.assertIn('name="EFI"', text)
        self.assertIn("uuid=BBBBBBBB-1111-2222-3333-444444444444", text)
        self.assertIn("uuid=CCCCCCCC-1111-2222-3333-444444444444", text)
        self.assertIn('attrs="RequiredPartition"', text)
        # New partitions take the lowest unused numbers.
        self.assertEqual(plan.swap.number, 4)
        self.assertEqual(plan.root.number, 5)

    def test_blank_disk_creates_esp_swap_root(self):
        table = disk.parse_sfdisk_json(
            fixture("sfdisk-gpt-blank.json"), device="/dev/vda", total_sectors=41943040
        )
        region = disk.find_free_regions(table, 41943040)[0]
        plan = disk.plan_layout(
            table, region, disk_path="/dev/vda", total_sectors=41943040
        )
        self.assertFalse(plan.esp.existing)
        self.assertEqual(plan.esp.size, 2097152)  # 1 GiB at 512-byte sectors
        self.assertEqual(plan.esp.number, 1)
        self.assertEqual(plan.esp.start, region.start)
        self.assertIsNotNone(plan.swap)
        self.assertEqual(plan.swap.number, 2)
        self.assertEqual(plan.root.number, 3)
        self.assertEqual(disk.validate_plan(plan), [])
        self.assertTrue(plan.esp.fs_uuid)
        self.assertRegex(plan.esp.fs_uuid or "", r"^[0-9A-F]{4}-[0-9A-F]{4}$")

    def test_swap_skipped_when_region_too_small(self):
        table = blank_table()
        # 9.5 GiB: ESP 512 + root 8 GiB fit, but not another 2 GiB.
        total = (9 * 1024 + 512) * 1024 * 1024 // 512
        table = blank_table(total_sectors=total)
        region = disk.find_free_regions(table, total)[0]
        plan = disk.plan_layout(
            table, region, disk_path="/dev/vda", total_sectors=total
        )
        self.assertIsNone(plan.swap)
        self.assertGreaterEqual((plan.root.size * plan.unit) // MIB, 8192)
        self.assertTrue(any("swap skipped" in warning for warning in plan.warnings))
        self.assertEqual(disk.validate_plan(plan), [])

    def test_too_small_region_raises(self):
        total = (8 * 1024) * 1024 * 1024 // 512
        table = blank_table(total_sectors=total)
        region = disk.find_free_regions(table, total)[0]
        with self.assertRaises(PlanError):
            disk.plan_layout(table, region, disk_path="/dev/vda", total_sectors=total)

    def test_custom_root_leaves_remainder(self):
        table = windows_table()
        region = disk.find_free_regions(table, 41943040)[0]
        plan = disk.plan_layout(
            table,
            region,
            disk_path="/dev/vda",
            total_sectors=41943040,
            root_mib=8192,
        )
        self.assertEqual((plan.root.size * plan.unit) // MIB, 8192)
        self.assertTrue(any("unallocated" in warn for warn in plan.warnings))
        self.assertEqual(disk.validate_plan(plan), [])

    def test_custom_root_below_minimum_raises(self):
        table = windows_table()
        region = disk.find_free_regions(table, 41943040)[0]
        with self.assertRaises(PlanError):
            disk.plan_layout(
                table,
                region,
                disk_path="/dev/vda",
                total_sectors=41943040,
                root_mib=4096,
            )

    def test_mbr_is_refused(self):
        table = disk.parse_sfdisk_json(
            fixture("sfdisk-dos.json"), device="/dev/vdc", total_sectors=41943040
        )
        region = disk.find_free_regions(table, 41943040)[0]
        with self.assertRaises(PlanError):
            disk.plan_layout(
                table, region, disk_path="/dev/vdc", total_sectors=41943040
            )

    def test_delete_middle_partition_and_reuse_number(self):
        table = windows_table()
        regions = disk.find_free_regions(table.without([2]), 41943040)
        region = max(regions, key=lambda item: item.size)
        plan = disk.plan_layout(
            table,
            region,
            disk_path="/dev/vda",
            total_sectors=41943040,
            delete_numbers=[2],
        )
        self.assertNotIn("BBBBBBBB-1111-2222-3333-444444444444", plan.new_table_text)
        self.assertIn("uuid=AAAAAAAA-1111-2222-3333-444444444444", plan.new_table_text)
        self.assertIn("uuid=CCCCCCCC-1111-2222-3333-444444444444", plan.new_table_text)
        self.assertEqual(disk.validate_plan(plan), [])

    def test_4kn_new_esp_size_and_fat_sector_flag(self):
        total = 5242880
        table = PartitionTable(
            device="/dev/vdd",
            label="gpt",
            id="DDDDDDDD-CCCC-BBBB-AAAA-999999999999",
            unit=4096,
            firstlba=256,
            lastlba=total - 34,
            total_sectors=total,
        )
        region = disk.find_free_regions(table, total)[0]
        plan = disk.plan_layout(
            table, region, disk_path="/dev/vdd", total_sectors=total
        )
        self.assertEqual(plan.esp.size, 262144)  # 1 GiB in 4K sectors
        self.assertEqual(plan.esp.start % 256, 0)
        self.assertEqual(plan.root.start % 256, 0)
        commands = disk.format_commands(plan)
        esp_cmd = next(c for c in commands if c.argv[0] == "mkfs.fat")
        self.assertIn("-S", esp_cmd.argv)
        self.assertIn("4096", esp_cmd.argv)
        self.assertEqual(disk.validate_plan(plan), [])


class VerifyPreservedTest(unittest.TestCase):
    def test_unchanged_is_clean(self):
        before = windows_table()
        after = windows_table()
        self.assertEqual(disk.verify_preserved(before, after), [])

    def test_deleted_partition_is_ignored(self):
        before = windows_table()
        after = windows_table().without([2])
        self.assertEqual(
            disk.verify_preserved(before, after, deleted=[2], allowed_new=[]), []
        )

    def test_changed_uuid_is_detected(self):
        before = windows_table()
        changed = dataclasses.replace(
            before.partitions[0],
            partuuid="FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF",
        )
        after = dataclasses.replace(
            before, partitions=(changed,) + before.partitions[1:]
        )
        issues = disk.verify_preserved(before, after)
        self.assertTrue(any("UUID changed" in issue for issue in issues))

    def test_changed_start_and_name_are_detected(self):
        before = windows_table()
        changed = dataclasses.replace(before.partitions[2], start=999, name="Other")
        after = dataclasses.replace(
            before, partitions=before.partitions[:2] + (changed,)
        )
        issues = disk.verify_preserved(before, after)
        self.assertTrue(any("start changed" in issue for issue in issues))
        self.assertTrue(any("name changed" in issue for issue in issues))

    def test_unexpected_new_partition_is_detected(self):
        before = windows_table()
        new = disk.Partition(node="/dev/vda9", number=9, start=40000000, size=2048)
        after = dataclasses.replace(before, partitions=before.partitions + (new,))
        issues = disk.verify_preserved(before, after)
        self.assertTrue(any("unexpected new partition 9" in issue for issue in issues))

    def test_deleted_partition_still_present_is_detected(self):
        before = windows_table()
        after = windows_table()  # partition 2 was supposed to be deleted
        issues = disk.verify_preserved(before, after, deleted=[2], allowed_new=[])
        self.assertTrue(any("partition 2 was not deleted" in issue for issue in issues))

    def test_deleted_number_reused_by_a_planned_partition_is_allowed(self):
        before = windows_table()
        after = windows_table().without([2])
        # The plan reuses number 2 for swap; the presence of a new #2 is
        # checked by verify_planned, not flagged as a failed deletion.
        issues = disk.verify_preserved(before, after, deleted=[2], allowed_new=[2])
        self.assertFalse(any("not deleted" in issue for issue in issues))

    def test_verify_planned(self):
        table = disk.parse_sfdisk_json(
            fixture("sfdisk-gpt-blank.json"), device="/dev/vda", total_sectors=41943040
        )
        region = disk.find_free_regions(table, 41943040)[0]
        plan = disk.plan_layout(
            table, region, disk_path="/dev/vda", total_sectors=41943040
        )
        parts = tuple(
            disk.Partition(
                node=part.node,
                number=part.number,
                start=part.start,
                size=part.size,
                type=part.type,
                partuuid=part.partuuid,
            )
            for part in plan.new_partitions
        )
        after = PartitionTable(
            device="/dev/vda",
            label="gpt",
            id=plan.disk_id,
            unit=plan.unit,
            firstlba=plan.first_lba,
            lastlba=plan.last_lba,
            total_sectors=plan.total_sectors,
            partitions=parts,
        )
        self.assertEqual(disk.verify_planned(plan, after), [])
        broken = dataclasses.replace(
            after,
            partitions=(
                dataclasses.replace(parts[0], size=parts[0].size + 2048),
            )
            + parts[1:],
        )
        issues = disk.verify_planned(plan, broken)
        self.assertTrue(any("size changed" in issue for issue in issues))


class CommandsTest(unittest.TestCase):
    def _plan(self):
        table = windows_table()
        region = disk.find_free_regions(table, 41943040)[0]
        return disk.plan_layout(
            table, region, disk_path="/dev/vda", total_sectors=41943040
        )

    def _blank_plan(self):
        table = disk.parse_sfdisk_json(
            fixture("sfdisk-gpt-blank.json"), device="/dev/vda", total_sectors=41943040
        )
        region = disk.find_free_regions(table, 41943040)[0]
        return disk.plan_layout(
            table, region, disk_path="/dev/vda", total_sectors=41943040
        )

    def test_snapshot_precedes_write_and_mkfs(self):
        plan = self._blank_plan()
        commands = disk.partition_commands(plan) + disk.format_commands(plan)
        argvs = [c.argv for c in commands]
        dump = next(i for i, a in enumerate(argvs) if a[:2] == ("sfdisk", "--dump"))
        backup = next(
            i for i, a in enumerate(argvs) if "--backup-pt-sectors" in a
        )
        write = next(
            i for i, a in enumerate(argvs) if a[:3] == ("sfdisk", "--no-reread", "--lock=yes")
        )
        verify = next(
            i for i, a in enumerate(argvs) if a[:2] == ("sfdisk", "--verify")
        )
        mkfs = next(i for i, a in enumerate(argvs) if a[0] == "mkfs.fat")
        mke2fs = next(i for i, a in enumerate(argvs) if a[0] == "mke2fs")
        self.assertLess(dump, backup)
        self.assertLess(backup, write)
        self.assertLess(write, verify)
        self.assertLess(verify, mkfs)
        self.assertLess(mkfs, mke2fs)

    def test_write_command_contains_full_gpt(self):
        plan = self._plan()
        write = next(
            c
            for c in disk.write_table_commands(plan)
            if c.argv[:3] == ("sfdisk", "--no-reread", "--lock=yes")
        )
        self.assertFalse(write.stdin_redacted)
        self.assertTrue(write.stdin.startswith("label: gpt\n"))
        self.assertIn("label-id: 11111111-2222-3333-4444-555555555555", write.stdin)
        self.assertIn("uuid=AAAAAAAA-1111-2222-3333-444444444444", write.stdin)

    def test_rollback_uses_snapshot_stdin(self):
        plan = self._plan()
        commands = disk.rollback_commands(plan)
        self.assertEqual(commands[0].argv[:2], ("sfdisk", "--no-reread"))
        self.assertTrue(commands[0].stdin_path.endswith(".sfdisk"))

    def test_plan_dict_is_json_serializable(self):
        payload = self._plan().to_dict()
        text = json.dumps(payload, sort_keys=True)
        self.assertIn('"root"', text)
        self.assertEqual(payload["disk"], "/dev/vda")

    def test_validate_detects_small_root(self):
        plan = self._plan()
        broken = dataclasses.replace(
            plan,
            root=dataclasses.replace(plan.root, size=1024),
        )
        issues = disk.validate_plan(broken)
        self.assertTrue(any("root is smaller" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
