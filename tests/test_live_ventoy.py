import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALLER = os.path.join(REPO_ROOT, "package_specs", "tenko-installer")
MODULE = os.path.join(INSTALLER, "files")


def read(relative):
    with open(os.path.join(REPO_ROOT, relative), encoding="utf-8") as handle:
        return handle.read()


class LiveVentoyTest(unittest.TestCase):
    """Ventoy chain-loads systemd-boot, so the live initramfs has to find the
    ISO file itself; these checks keep that fallback wired into the package
    without delaying a normal CD or dd-written USB boot."""

    def test_live_dracut_config_enables_the_module(self):
        conf = read("package_specs/tenko-installer/files/20-tenko-live.conf")
        self.assertIn("dmsquash-live", conf)
        self.assertIn("tenko-ventoy", conf)

    def test_module_setup_installs_script_and_rule(self):
        setup = read(
            "package_specs/tenko-installer/files/"
            "95tenko-ventoy.module-setup.sh")
        self.assertIn('inst_simple "$moddir/tenko-ventoy-iso.sh" '
                      '/sbin/tenko-ventoy-iso', setup)
        self.assertIn('inst_rules "$moddir/tenko-ventoy.rules"', setup)
        # An unconditional initqueue hook would sleep on every normal boot.
        self.assertNotIn("inst_hook initqueue", setup)
        # Ventoy's data partition is exFAT by default; NTFS and FAT are also
        # offered by the installer.
        for module in ("exfat", "vfat", "ntfs3"):
            self.assertIn(module, setup)

    def test_rule_is_ventoy_only(self):
        rules = read(
            "package_specs/tenko-installer/files/95tenko-ventoy.rules")
        self.assertIn('ENV{ID_FS_LABEL}=="VTOYEFI"', rules)
        self.assertIn("/sbin/tenko-ventoy-iso", rules)
        self.assertIn("initqueue", rules)

    def test_scan_skips_real_media_and_drives_dmsquash(self):
        scan = read(
            "package_specs/tenko-installer/files/95tenko-ventoy.iso-scan.sh")
        self.assertIn('TENKO_LABEL=TENKO', scan)
        # A real CD or dd-written stick already has the label.
        self.assertIn('"/dev/disk/by-label/$TENKO_LABEL" ] && exit 0', scan)
        # udev may create the label after the initqueue has settled, so the
        # live root is set up directly instead of waiting for the rule.
        self.assertIn('/sbin/dmsquash-live-root "$loop"', scan)

    def test_spec_ships_the_module_and_bumps_the_release(self):
        spec = read("package_specs/tenko-installer/tenko-installer.spec")
        self.assertIn("%dir /usr/lib/dracut/modules.d/95tenko-ventoy", spec)
        for name in ("module-setup.sh", "tenko-ventoy-iso.sh",
                     "tenko-ventoy.rules"):
            self.assertIn("95tenko-ventoy/" + name, spec)
        self.assertIn("95tenko-ventoy.module-setup.sh", spec)
        self.assertIn("95tenko-ventoy.iso-scan.sh", spec)
        self.assertIn("95tenko-ventoy.rules", spec)
        # The Ventoy module landed in 6-12; later installer fixes may bump the
        # release further, so only require that it has not gone backwards.
        release = re.search(r"^Release:\s+(\d+)", spec, re.MULTILINE)
        self.assertIsNotNone(release)
        self.assertGreaterEqual(int(release.group(1)), 12)
        self.assertIn("#49", spec)

    def test_module_files_exist(self):
        for name in ("95tenko-ventoy.module-setup.sh",
                     "95tenko-ventoy.iso-scan.sh",
                     "95tenko-ventoy.rules"):
            self.assertTrue(os.path.isfile(os.path.join(MODULE, name)), name)


if __name__ == "__main__":
    unittest.main()
