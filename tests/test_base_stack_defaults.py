import json
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")

# Requested base OS packages: storage (udisks2 + its libblockdev backend),
# firmware updates and the diagnostic/editor tools.
BASE_PACKAGES = ("lsof", "strace", "nano", "libblockdev", "udisks2", "fwupd")

# Requested desktop-profile packages: panel volume control and VA-API.
DESKTOP_PACKAGES = ("xfce4-pulseaudio-plugin", "libva")


def read(relative):
    with open(os.path.join(SPECS, relative), encoding="utf-8") as handle:
        return handle.read()


def spec_lines(relative):
    lines = read(relative).splitlines()
    changelog = next((i for i, line in enumerate(lines)
                      if line.startswith("%changelog")), len(lines))
    return lines[:changelog]


def has_require(lines, name):
    pattern = re.compile(r"^Requires:\s+%s\s*$" % re.escape(name))
    return any(pattern.match(line) for line in lines)


class BaseStackDefaultsTest(unittest.TestCase):
    """The base set carries storage, firmware and diagnostics; the desktop
    profile adds the sound and VA-API packages.  Changing either split is a
    policy change, so guard it here."""

    def test_base_membership_and_rebuild_order(self):
        base = json.loads(read("base.json"))
        for name in BASE_PACKAGES:
            self.assertIn(name, base["packages"],
                          "%s must be base membership" % name)
            self.assertIn(name, base["build_order"],
                          "%s must be in the base rebuild order" % name)

    def test_libblockdev_precedes_udisks2(self):
        order = json.loads(read("base.json"))["build_order"]
        self.assertLess(order.index("libblockdev"), order.index("udisks2"))

    def test_tenko_base_and_runtime_require_base_packages(self):
        for spec in ("tenko-base/tenko-base.spec",
                     "tenko-base-runtime/tenko-base-runtime.spec"):
            lines = spec_lines(spec)
            for name in BASE_PACKAGES:
                self.assertTrue(
                    has_require(lines, name),
                    "%s must require %s" % (spec, name))

    def test_desktop_profile_requires_media_packages(self):
        lines = spec_lines("xfce-desktop/xfce-desktop.spec")
        for name in DESKTOP_PACKAGES:
            self.assertTrue(
                has_require(lines, name),
                "xfce-desktop must require %s" % name)

    def test_every_default_package_has_a_spec(self):
        for name in BASE_PACKAGES + DESKTOP_PACKAGES:
            spec = os.path.join(SPECS, name, name + ".spec")
            self.assertTrue(os.path.isfile(spec), "missing spec for " + name)


if __name__ == "__main__":
    unittest.main()
