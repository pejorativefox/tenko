"""Tests for the guided-flow helpers and direct partition actions."""

from __future__ import annotations

import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "files"))

import disk  # noqa: E402
import layout  # noqa: E402
import main  # noqa: E402
from install import InstallConfig  # noqa: E402


class FakeUI:
    def __init__(self, answers):
        self.answers = list(answers)
        self.menus = []
        self.messages = []
        self.forms = []

    def menu(self, title, subtitle, rows, **kwargs):
        self.menus.append((title, [row.text for row in rows]))
        return self.answers.pop(0)

    def form(self, title, fields, **kwargs):
        self.forms.append((title, [field.label for field in fields]))
        return self.answers.pop(0)

    def message(self, title, lines, **kwargs):
        self.messages.append((title, list(lines)))
        return 0


def one_partition_table():
    part = disk.Partition(
        node="/dev/vdb1",
        number=1,
        start=2048,
        size=2097152,
        type=disk.ESP_TYPE,
        partuuid="11111111-1111-1111-1111-111111111111",
        name="EFI",
        fs_uuid="1234-ABCD",
        fstype="vfat",
        label="EFI",
    )
    return disk.PartitionTable(
        device="/dev/vdb",
        label="gpt",
        id="22222222-2222-2222-2222-222222222222",
        unit=512,
        firstlba=2048,
        lastlba=41943006,
        total_sectors=41943040,
        partitions=(part,),
    ), part


class ParseSizeTest(unittest.TestCase):
    def test_bare_number_is_gib(self):
        self.assertEqual(main._parse_size_mib("20"), 20480)
        self.assertEqual(main._parse_size_mib("1.5"), 1536)

    def test_explicit_units(self):
        self.assertEqual(main._parse_size_mib("512M"), 512)
        self.assertEqual(main._parse_size_mib("512MiB"), 512)
        self.assertEqual(main._parse_size_mib("20G"), 20480)
        self.assertEqual(main._parse_size_mib("20GiB"), 20480)

    def test_blank_is_none(self):
        self.assertIsNone(main._parse_size_mib("  "))

    def test_invalid_is_rejected(self):
        for value in ("abc", "-1", "0", "12wat"):
            with self.assertRaises(ValueError):
                main._parse_size_mib(value)


class DiskMapTest(unittest.TestCase):
    def test_existing_disk_shows_segments_and_free_space(self):
        table, _part = one_partition_table()
        lines = main._disk_map_lines(table, 72)
        self.assertEqual(len(lines), 2)
        self.assertIn("ESP", lines[0])
        self.assertIn("free", lines[0])
        self.assertIn("ESP 1.0 GiB", lines[1])
        self.assertIn("free", lines[1])

    def test_blank_disk_is_a_single_free_segment(self):
        table, _part = one_partition_table()
        blank = disk.PartitionTable(
            device="/dev/vdb",
            label="gpt",
            id=table.id,
            unit=512,
            firstlba=2048,
            lastlba=41943006,
            total_sectors=41943040,
            partitions=(),
        )
        lines = main._disk_map_lines(blank, 72)
        self.assertIn("free", lines[0])
        self.assertIn("free 20.0 GiB", lines[1])


class AccountFlowTest(unittest.TestCase):
    def test_password_mismatch_returns_to_the_account_form(self):
        spec = layout.InstallSpec(
            disks=(
                layout.DiskSpec(
                    path="/dev/vda",
                    partitions=(
                        layout.PartitionSpec(
                            "esp", "vfat", "/boot", size_mib=1024
                        ),
                        layout.PartitionSpec("root", "ext4", "/"),
                    ),
                ),
            )
        )
        config = InstallConfig(
            layout=spec,
            confirm_disk="/dev/vda",
            confirm_phrase="ERASE",
            swap_mode="swapfile",
        )
        ui = FakeUI(
            [
                0,
                ["myhost", "myuser", "one", "two"],
                ["myhost", "myuser", "same", "same"],
            ]
        )
        self.assertTrue(main._account_and_packages(ui, config))
        self.assertEqual(config.admin_password, "same")
        self.assertEqual(len(ui.menus), 1)
        self.assertEqual(len(ui.forms), 2)
        self.assertEqual(len(ui.messages), 1)
        self.assertEqual(
            ui.messages[0][0], "Passwords do not match"
        )


class PartitionActionsTest(unittest.TestCase):
    def test_delete_selected_partition_without_typing_its_number(self):
        table, part = one_partition_table()
        specs = []
        delete_set = set()
        ui = FakeUI([1, 0])  # "Delete this partition", then "Yes, delete it"
        main._partition_actions(ui, table, part, specs, delete_set)
        self.assertEqual(delete_set, {1})
        self.assertEqual(specs, [])
        self.assertIn("Partition 1 on /dev/vdb", ui.menus[0][0])
        self.assertIn("Delete this partition", ui.menus[0][1])

    def test_cancel_a_marked_deletion(self):
        table, part = one_partition_table()
        specs = []
        delete_set = {1}
        ui = FakeUI([0])  # "Keep this partition"
        main._partition_actions(ui, table, part, specs, delete_set)
        self.assertEqual(delete_set, set())


if __name__ == "__main__":
    unittest.main()
