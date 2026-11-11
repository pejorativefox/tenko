import os
import re
import unittest

from specutil import expand_if_spec as _expand_spec

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")


def spec_lines(relative):
    with open(os.path.join(SPECS, relative), encoding="utf-8") as handle:
        lines = _expand_spec(handle.read(), os.path.join(SPECS, relative)).splitlines()
    changelog = next((i for i, line in enumerate(lines)
                      if line.startswith("%changelog")), len(lines))
    return lines[:changelog]


def has_require(lines, name):
    pattern = re.compile(r"^Requires:\s+%s\s*$" % re.escape(name))
    return any(pattern.match(line) for line in lines)


class DesktopNetworkTest(unittest.TestCase):
    """Desktop installs bring their own networking: NetworkManager runs on
    boot and nm-applet is installed so xfce4-session can autostart it."""

    def test_desktop_profiles_require_network_manager_and_applet(self):
        for spec in ("xfce-desktop/xfce-desktop.spec",
                     "xfce-desktop-core/xfce-desktop-core.spec"):
            lines = spec_lines(spec)
            for package in ("NetworkManager", "network-manager-applet"):
                self.assertTrue(
                    has_require(lines, package),
                    "%s must require %s" % (spec, package))

    def test_applet_ships_xdg_autostart_entry(self):
        # This is the file xfce4-session reads from XDG_CONFIG_DIRS at login.
        spec = "network-manager-applet/network-manager-applet.spec"
        self.assertIn("/etc/xdg/autostart/nm-applet.desktop",
                      spec_lines(spec))

    def test_network_manager_preset_enables_the_service(self):
        preset = os.path.join(SPECS, "networkmanager", "files",
                              "40-tenko-networkmanager.preset")
        with open(preset, encoding="utf-8") as handle:
            rules = [line.strip() for line in handle
                     if line.strip() and not line.startswith("#")]
        self.assertIn("enable NetworkManager.service", rules)
        self.assertIn("disable systemd-networkd.service", rules)


if __name__ == "__main__":
    unittest.main()
