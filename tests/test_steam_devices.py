import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")


def read(relative):
    with open(os.path.join(SPECS, relative), encoding="utf-8") as handle:
        return handle.read()


def spec_lines(relative):
    with open(os.path.join(SPECS, relative), encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    changelog = next((i for i, line in enumerate(lines)
                      if line.startswith("%changelog")), len(lines))
    return lines[:changelog]


def has_require(lines, name):
    pattern = re.compile(r"^Requires:\s+%s\s*$" % re.escape(name))
    return any(pattern.match(line) for line in lines)


class SteamDevicesTest(unittest.TestCase):
    """The default desktop ships Valve's controller udev rules, so the Steam
    Flatpak finds /dev/uinput writable instead of warning that
    "steam-devices" is missing."""

    def test_rules_are_installed(self):
        spec = read("steam-devices/steam-devices.spec")
        for rule in ("60-steam-input.rules", "60-steam-vr.rules"):
            self.assertIn(
                "%{_udevrulesdir}/" + rule, spec,
                "%s must be installed into the udev rules directory" % rule)
        self.assertIn("%license LICENSE", spec)

    def test_udev_is_reloaded_after_install(self):
        # This systemd package has no udev file trigger, so the scriptlet is
        # the only thing that applies the new permissions to the live node.
        spec = read("steam-devices/steam-devices.spec")
        self.assertIn("udevadm control --reload", spec)
        self.assertIn("udevadm trigger", spec)
        self.assertIn("--sysname-match=uinput", spec)

    def test_source_is_pinned_snapshot(self):
        # Upstream's newest tag (v1.0.0.61) is from 2019; the master snapshot
        # carries current controller support.  Keep both the commit and the
        # hash pinned so a refresh is an explicit change.
        sources = read("steam-devices/sources")
        self.assertIn("1396759ece4ba44ab47e39b48e203a5b", sources)
        self.assertIn(
            "22ec85e5ff5ea2e15c56d71a41bcbef46356cd60", sources)
        self.assertIn("steam-devices-20260625.tar.gz", sources)

    def test_desktop_profiles_require_steam_devices(self):
        for spec in ("xfce-desktop/xfce-desktop.spec",
                     "xfce-desktop-core/xfce-desktop-core.spec"):
            self.assertTrue(
                has_require(spec_lines(spec), "steam-devices"),
                "%s must require steam-devices" % spec)


if __name__ == "__main__":
    unittest.main()
