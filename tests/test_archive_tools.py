import json
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(relative):
    with open(os.path.join(REPO_ROOT, relative), encoding="utf-8") as handle:
        return handle.read()


def spec(name):
    return read(os.path.join("package_specs", name, name + ".spec"))


def extra_requires():
    text = read("package_specs/tenko-base/requires-extra")
    return [line.split("#", 1)[0].strip()
            for line in text.splitlines()
            if line.split("#", 1)[0].strip()]


class ArchiveToolsTest(unittest.TestCase):
    """zip and unzip are base packages, so every install can create and
    extract .zip archives."""

    def test_zip_and_unzip_are_base_membership(self):
        base = json.loads(read("package_specs/base.json"))
        for name in ("zip", "unzip"):
            self.assertIn(name, base["packages"])
            self.assertIn(name, base["build_order"])

    def test_not_an_extra(self):
        extras = extra_requires()
        for name in ("zip", "unzip"):
            self.assertNotIn(name, extras)

    def test_base_meta_requires_the_archive_tools(self):
        lines = spec("tenko-base")
        for name in ("zip", "unzip"):
            self.assertRegex(lines, r"(?m)^Requires:\s+%s\s*$" % re.escape(name))

    def test_runtime_meta_installs_the_archive_tools(self):
        # The installer and live ISO install tenko-base-runtime, not
        # tenko-base; base membership alone leaves zip/unzip off a fresh
        # install.
        lines = spec("tenko-base-runtime")
        for name in ("zip", "unzip"):
            self.assertRegex(lines, r"(?m)^Requires:\s+%s\s*$" % re.escape(name))


if __name__ == "__main__":
    unittest.main()
