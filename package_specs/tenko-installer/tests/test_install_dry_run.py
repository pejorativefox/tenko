"""Integration test: the entire install pipeline in dry-run mode.

No command from the mutation list is executed.  The test verifies that every
phase is represented in plan.sh for a two-disk layout (``/`` on /dev/vda,
``/home`` on /dev/vdb), including the basefs-first dnf transactions, the
chroot bootloader/dracut commands and the redacted chpasswd stdin.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "files"))

import disk  # noqa: E402
import layout  # noqa: E402
from install import InstallConfig, Installer  # noqa: E402
from log import Logger  # noqa: E402
from runner import CommandRunner  # noqa: E402

FIXTURES = HERE / "fixtures"
MIB = 1024 * 1024


class FakeProbe:
    def __init__(self, plan):
        self.plan = plan

    def resolve_partition(self, part):
        return part.by_partuuid

    def wait_for_partuuids(self, plan, timeout=15.0):
        return True


def _tables():
    raw = (FIXTURES / "sfdisk-gpt-blank.json").read_text(encoding="utf-8")
    vda = disk.parse_sfdisk_json(raw, device="/dev/vda", total_sectors=41943040)
    vdb = disk.parse_sfdisk_json(raw, device="/dev/vdb", total_sectors=41943040)
    return {"/dev/vda": vda, "/dev/vdb": vdb}


class DryRunPipelineTest(unittest.TestCase):
    def test_full_pipeline_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            spec = layout.InstallSpec(
                disks=(
                    layout.DiskSpec(
                        path="/dev/vda",
                        partitions=(
                            layout.PartitionSpec(
                                "esp", "vfat", "/boot", size_mib=1024
                            ),
                            layout.PartitionSpec("swap", "swap", None, size_mib=2048),
                            layout.PartitionSpec("root", "ext4", "/"),
                        ),
                    ),
                    layout.DiskSpec(
                        path="/dev/vdb",
                        partitions=(
                            layout.PartitionSpec("data", "btrfs", "/home"),
                        ),
                    ),
                )
            )
            plan = layout.plan_install(_tables(), spec)
            self.assertEqual(layout.validate_layout(plan), [])

            log_path = pathlib.Path(temp) / "install.jsonl"
            plan_path = pathlib.Path(temp) / "plan.sh"
            logger = Logger(
                str(log_path), human_path=str(pathlib.Path(temp) / "install.log")
            )
            self.addCleanup(logger.close)
            runner = CommandRunner(logger, dry_run=True, plan_path=str(plan_path))
            config = InstallConfig(
                layout=spec,
                package_set="desktop",
                hostname="tenko",
                timezone="Europe/Berlin",
                locale="C.UTF-8",
                keymap="de",
                admin_user="admin",
                admin_password="super-secret",
                confirm_disk="/dev/vda",
                confirm_phrase="ERASE",
                dry_run=True,
            )
            self.assertEqual(config.validate(), [])
            installer = Installer(config, runner, logger, FakeProbe(plan), plan)
            installer.run()

            text = plan_path.read_text(encoding="utf-8")
            self.assertIn("sfdisk --no-reread --lock=yes /dev/vda", text)
            self.assertIn("sfdisk --no-reread --lock=yes /dev/vdb", text)
            self.assertIn("mkfs.fat", text)
            self.assertIn("mke2fs", text)
            self.assertIn("mkswap", text)
            self.assertIn("mkfs.btrfs", text)
            self.assertIn("mount -o rw,noatime /dev/disk/by-partuuid/", text)
            self.assertIn(" /mnt/tenko", text)
            self.assertIn(" /mnt/tenko/boot", text)
            self.assertIn(" /mnt/tenko/home", text)
            self.assertIn("swapon", text)
            self.assertIn("UUID=", text)
            self.assertIn(" /home btrfs ", text)
            self.assertIn("--installroot /mnt/tenko", text)
            self.assertIn("install tenko-basefs", text)
            self.assertIn("install tenko-base-runtime xfce-desktop", text)
            self.assertIn("/usr/bin/bootctl", text)
            self.assertIn("--esp-path=/boot", text)
            self.assertIn("--no-variables", text)
            self.assertIn("systemd-bootx64.efi", text)
            self.assertIn("default tenko-*", text)
            self.assertIn("loader/entries/tenko-", text)
            self.assertIn("linux /vmlinuz-", text)
            self.assertIn("initrd /initramfs-", text)
            self.assertIn("root=UUID=", text)
            self.assertNotIn("grub", text)
            self.assertIn("dracut --force --no-hostonly", text)
            self.assertIn("tenko-6.repo", text)
            self.assertIn("[tenko-6]", text)
            self.assertIn("name=Tenko Linux 6 (Workstation)", text)
            self.assertIn("https://tenko.pjfox.xyz/packages/6/", text)
            self.assertIn("/etc/localtime", text)
            self.assertIn("zoneinfo/Europe/Berlin", text)
            self.assertIn("LANG=C.UTF-8", text)
            self.assertIn("KEYMAP=de", text)
            self.assertIn("chpasswd", text)
            self.assertIn("passwd -l root", text)
            self.assertIn("firstboot-root-password.done", text)
            self.assertIn("umount -R /mnt/tenko", text)
            self.assertNotIn("super-secret", text)

            log_text = log_path.read_text(encoding="utf-8")
            self.assertIn('"event": "step-done"', log_text)
            self.assertIn('"event": "install-complete"', log_text)
            self.assertNotIn("super-secret", log_text)

    def test_swapfile_is_created_without_a_swap_partition(self):
        with tempfile.TemporaryDirectory() as temp:
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
            plan = layout.plan_install(_tables(), spec)
            self.assertEqual(plan.swaps, ())

            plan_path = pathlib.Path(temp) / "plan.sh"
            logger = Logger(str(pathlib.Path(temp) / "install.jsonl"))
            self.addCleanup(logger.close)
            runner = CommandRunner(
                logger, dry_run=True, plan_path=str(plan_path)
            )
            config = InstallConfig(
                layout=spec,
                admin_password="secret",
                confirm_disk="/dev/vda",
                confirm_phrase="ERASE",
                dry_run=True,
                swap_mode="swapfile",
                swap_mib=1024,
            )
            self.assertEqual(config.validate(), [])
            Installer(config, runner, logger, FakeProbe(plan), plan).run()

            text = plan_path.read_text(encoding="utf-8")
            self.assertIn(
                "fallocate -l 1024M /mnt/tenko/swapfile", text
            )
            self.assertIn(
                "mkswap -L tenko-swap /mnt/tenko/swapfile", text
            )
            self.assertIn("swapon /mnt/tenko/swapfile", text)
            self.assertIn("/swapfile none swap sw 0 0", text)
            self.assertNotIn("mkswap -L tenko-swap -U", text)


if __name__ == "__main__":
    unittest.main()
