"""Tests for the synthetic-disk --simulate mode."""

from __future__ import annotations

import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "files"))

import disk  # noqa: E402
import layout  # noqa: E402
import main  # noqa: E402
import simulate  # noqa: E402
from install import InstallConfig  # noqa: E402
from log import null_logger  # noqa: E402
from runner import CommandRunner  # noqa: E402


class SimulatedDiskTest(unittest.TestCase):
    def test_blank_scenario(self):
        disks = simulate.synthesize("blank")
        self.assertEqual([item.disk.path for item in disks], ["/dev/vda", "/dev/vdb"])
        self.assertTrue(all(item.selectable for item in disks))
        self.assertTrue(all(not item.table.partitions for item in disks))
        self.assertTrue(all(item.table.is_gpt for item in disks))
        self.assertGreater(disks[0].disk.size_bytes, disks[1].disk.size_bytes)

    def test_mixed_scenario_has_an_esp_and_data_partition(self):
        disks = simulate.synthesize("mixed")
        table = disks[1].table
        self.assertIsNotNone(table)
        self.assertEqual([part.number for part in table.partitions], [1, 2])
        self.assertEqual(table.partitions[0].fstype, "vfat")
        self.assertEqual(table.partitions[1].fstype, "ext4")
        self.assertEqual(
            table.partitions[0].type.upper(), disk.ESP_TYPE
        )

    def test_unknown_scenario_is_rejected(self):
        with self.assertRaises(ValueError):
            simulate.synthesize("nope")


class SimulatedProbeTest(unittest.TestCase):
    def setUp(self):
        self.runner = CommandRunner(
            null_logger(), dry_run=True, plan_path="/tmp/sim-plan.sh"
        )

    def test_probe_shape(self):
        probe = simulate.SimulatedProbe(self.runner, "blank")
        self.assertTrue(probe.simulated)
        self.assertEqual(len(probe.probe_disks()), 2)
        self.assertIsNone(probe.detect_live_disk())
        self.assertFalse(probe.secure_boot_state())
        found = probe.find_disk("/dev/vdb")
        self.assertIsNotNone(found)
        self.assertFalse(probe.read_table(found).partitions)
        checks = probe.preflight(
            repo="unused", target="/tmp/target", live_kname=None
        )
        self.assertTrue(all(check.ok for check in checks))

    def test_mixed_disk_can_be_planned(self):
        probe = simulate.SimulatedProbe(self.runner, "mixed")
        spec = layout.InstallSpec(
            disks=(
                layout.DiskSpec(
                    path="/dev/vdb",
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
                        layout.PartitionSpec("root", "btrfs", "/"),
                    ),
                ),
            )
        )
        tables = {
            item.disk.path: probe.read_table(item)
            for item in probe.probe_disks()
        }
        plan = layout.plan_install(tables, spec)
        self.assertTrue(plan.esp.existing)
        self.assertEqual(plan.esp.number, 1)
        self.assertEqual(plan.find_mount("/home").number, 2)
        self.assertEqual(plan.root.fstype, "btrfs")

    def test_main_build_layout_uses_simulated_probe(self):
        probe = simulate.SimulatedProbe(self.runner, "blank")
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
                        layout.PartitionSpec("data", "ext4", "/home"),
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
        plan, probed, regions = main.build_layout(probe, config)
        self.assertEqual(len(probed), 2)
        self.assertEqual(set(regions), {"/dev/vda", "/dev/vdb"})
        self.assertEqual(plan.find_mount("/home").fstype, "ext4")

    def test_simulate_flag_forces_dry_run(self):
        args = main.parse_args(["--simulate"])
        self.assertTrue(args.simulate)
        self.assertTrue(args.dry_run)
        args = main.parse_args(["--simulate-scenario", "mixed"])
        self.assertTrue(args.simulate)
        self.assertEqual(args.simulate_scenario, "mixed")


if __name__ == "__main__":
    unittest.main()
