"""Integration test: the entire install pipeline in dry-run mode.

No command from the mutation list is executed.  The test verifies that every
phase is represented in plan.sh, including the basefs-first dnf transactions,
the chroot bootloader/dracut commands and the redacted chpasswd stdin.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "files"))

import disk  # noqa: E402
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

    def wait_for_partuuid(self, plan, timeout=15.0):
        return True


class DryRunPipelineTest(unittest.TestCase):
    def test_full_pipeline_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            raw = (FIXTURES / "sfdisk-gpt-blank.json").read_text(encoding="utf-8")
            table = disk.parse_sfdisk_json(
                raw, device="/dev/vda", total_sectors=41943040
            )
            region = disk.find_free_regions(table, 41943040)[0]
            plan = disk.plan_layout(
                table, region, disk_path="/dev/vda", total_sectors=41943040
            )
            self.assertEqual(disk.validate_plan(plan), [])

            log_path = pathlib.Path(temp) / "install.jsonl"
            plan_path = pathlib.Path(temp) / "plan.sh"
            logger = Logger(
                str(log_path), human_path=str(pathlib.Path(temp) / "install.log")
            )
            self.addCleanup(logger.close)
            runner = CommandRunner(logger, dry_run=True, plan_path=str(plan_path))
            config = InstallConfig(
                disk_path="/dev/vda",
                delete_partitions=(),
                esp_mib=512,
                root_mib=None,
                swap_mib=2048,
                package_set="desktop",
                hostname="browneye",
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
            self.assertIn("mkfs.fat", text)
            self.assertIn("mke2fs", text)
            self.assertIn("mkswap", text)
            self.assertIn("--installroot /mnt/browneye", text)
            self.assertIn("install browneye-basefs", text)
            self.assertIn("install browneye-base-runtime xfce-desktop", text)
            self.assertIn("/usr/bin/bootctl", text)
            self.assertIn("--esp-path=/boot", text)
            self.assertIn("--no-variables", text)
            self.assertIn("systemd-bootx64.efi", text)
            self.assertIn("default browneye-*", text)
            self.assertIn("loader/entries/browneye-", text)
            self.assertIn("linux /vmlinuz-", text)
            self.assertIn("initrd /initramfs-", text)
            self.assertIn("root=UUID=", text)
            self.assertNotIn("grub", text)
            self.assertIn("dracut --force --no-hostonly", text)
            self.assertIn("browneye-13.1.repo", text)
            self.assertIn("https://tomfool.8bit.ca/browneye/packages/13.1/", text)
            self.assertIn("chpasswd", text)
            self.assertIn("passwd -l root", text)
            self.assertIn("firstboot-root-password.done", text)
            self.assertIn("umount -R /mnt/browneye", text)
            self.assertNotIn("super-secret", text)

            log_text = log_path.read_text(encoding="utf-8")
            self.assertIn('"event": "step-done"', log_text)
            self.assertIn('"event": "install-complete"', log_text)
            self.assertNotIn("super-secret", log_text)


if __name__ == "__main__":
    unittest.main()
