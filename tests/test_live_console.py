"""The live console must stay on the installer, with a root rescue shell."""

import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = os.path.join(REPO_ROOT, "package_specs", "tenko-installer", "files")
SPEC = os.path.join(
    REPO_ROOT, "package_specs", "tenko-installer", "tenko-installer.spec")
BUILD = os.path.join(REPO_ROOT, "scripts", "build_iso_uefi.sh")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


class LivePresetTest(unittest.TestCase):
    def test_preset_sorts_before_the_kmscon_preset(self):
        preset = os.path.join(FILES, "45-tenko-live.preset")
        self.assertTrue(os.path.isfile(preset))
        self.assertFalse(
            os.path.isfile(os.path.join(FILES, "90-tenko-live.preset"))
        )
        self.assertLess(
            os.path.basename(preset),
            "50-tenko-console.preset",
        )

    def test_preset_keeps_tty1_for_the_installer(self):
        preset = read(os.path.join(FILES, "45-tenko-live.preset"))
        self.assertIn("disable kmsconvt@tty1.service", preset)
        self.assertIn("disable tenko-firstboot-root-password.service", preset)
        self.assertIn("enable tenko-installer.service", preset)

    def test_spec_installs_the_early_preset(self):
        spec = read(SPEC)
        self.assertIn("45-tenko-live.preset", spec)


class LiveRescueShellTest(unittest.TestCase):
    def test_image_enables_passwordless_root_shells(self):
        build = read(BUILD)
        self.assertIn("getty@tty2.service.d/autologin.conf", build)
        self.assertIn("--autologin root", build)
        self.assertIn("serial-getty@ttyS0.service.d/autologin.conf", build)
        self.assertIn("root::", build)
        # The instance mask protects against a preset-order regression.
        self.assertIn("kmsconvt@tty1.service", build)
        # The kmscon nmtui VT must not get a competing login.
        self.assertIn("getty@tty3.service", build)
        self.assertIn("kmsconvt@tty3.service", build)


if __name__ == "__main__":
    unittest.main()
