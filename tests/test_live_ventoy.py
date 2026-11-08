import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALLER = os.path.join(REPO_ROOT, "package_specs", "tenko-installer")


def read(relative):
    with open(os.path.join(REPO_ROOT, relative), encoding="utf-8") as handle:
        return handle.read()


class LiveVentoyTest(unittest.TestCase):
    """Ventoy chain-loads systemd-boot, so the live initramfs has to find the
    ISO file itself; these checks keep that fallback wired into the package."""

    def test_live_dracut_config_enables_the_module(self):
        conf = read("package_specs/tenko-installer/files/20-tenko-live.conf")
        self.assertIn("dmsquash-live", conf)
        self.assertIn("tenko-ventoy", conf)

    def test_module_setup_installs_the_scan_hook(self):
        setup = read(
            "package_specs/tenko-installer/files/"
            "95tenko-ventoy.module-setup.sh")
        self.assertIn('inst_hook initqueue 05', setup)
        self.assertIn('"$moddir/tenko-ventoy-iso.sh"', setup)
        # Ventoy's data partition is exFAT by default; NTFS and FAT are also
        # offered by the installer.
        for module in ("exfat", "vfat", "ntfs3"):
            self.assertIn(module, setup)

    def test_scan_only_runs_for_ventoy_and_skips_real_media(self):
        scan = read(
            "package_specs/tenko-installer/files/95tenko-ventoy.iso-scan.sh")
        self.assertIn('TENKO_LABEL=TENKO', scan)
        self.assertIn('VTOY_LABEL=VTOYEFI', scan)
        # A real CD or dd-written stick already has the label.
        self.assertIn('"/dev/disk/by-label/$TENKO_LABEL" ] && exit 0', scan)
        # Without VTOYEFI this must not scan or wait.
        self.assertIn('"/dev/disk/by-label/$VTOY_LABEL"', scan)
        # dmsquash-live has to be driven directly: udev may create the label
        # after the initqueue has already settled.
        self.assertIn('/sbin/dmsquash-live-root "$loop"', scan)

    def test_spec_ships_the_module_and_bumps_the_release(self):
        spec = read("package_specs/tenko-installer/tenko-installer.spec")
        self.assertIn("%dir /usr/lib/dracut/modules.d/95tenko-ventoy", spec)
        self.assertIn("95tenko-ventoy/module-setup.sh", spec)
        self.assertIn("95tenko-ventoy/tenko-ventoy-iso.sh", spec)
        self.assertIn("95tenko-ventoy.module-setup.sh", spec)
        self.assertIn("95tenko-ventoy.iso-scan.sh", spec)
        self.assertIn("Release:    6", spec)
        self.assertIn("#49", spec)

    def test_module_files_exist(self):
        for name in ("95tenko-ventoy.module-setup.sh",
                     "95tenko-ventoy.iso-scan.sh"):
            self.assertTrue(os.path.isfile(os.path.join(INSTALLER, "files",
                                                        name)), name)


if __name__ == "__main__":
    unittest.main()
