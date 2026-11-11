"""The live installer must carry enough firmware for network setup."""

import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(REPO_ROOT, "package_specs", "tenko-live", "tenko-live.spec")


class LiveFirmwareTest(unittest.TestCase):
    def test_wifi_and_nic_firmware_are_real_requires(self):
        with open(SPEC, encoding="utf-8") as handle:
            spec = handle.read()
        # tenko image iso installs with install_weak_deps=False, so a
        # Recommends here would leave Wi-Fi without firmware on the media.
        for package in (
            "linux-firmware-intel-wifi",
            "linux-firmware-ath",
            "linux-firmware-mediatek",
            "linux-firmware-other",
            "linux-firmware-nic",
        ):
            self.assertIn("Requires:   " + package, spec)


if __name__ == "__main__":
    unittest.main()
