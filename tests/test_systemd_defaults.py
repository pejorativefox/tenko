"""logind leaves user processes running after the last session exits."""

import os
import re
import unittest

from specutil import read_spec

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(REPO_ROOT, "package_specs", "systemd", "systemd.spec")


class SystemdDefaultsTest(unittest.TestCase):
    def section(self, name):
        text = read_spec(SPEC)
        match = re.search(
            r"^%" + name + r"\n(.*?)(?=^%[a-z]|\Z)", text, re.M | re.S)
        self.assertIsNotNone(match, "systemd spec must have a %" + name)
        return "\n".join(line for line in match.group(1).splitlines()
                         if not line.lstrip().startswith("#"))

    def test_build_explicitly_disables_killing_user_processes(self):
        self.assertRegex(
            self.section("build"), r"-D\s*default-kill-user-processes=false\b",
            "%build must explicitly select KillUserProcesses=no")

    def test_build_does_not_enable_killing_user_processes(self):
        self.assertNotRegex(
            self.section("build"), r"-D\s*default-kill-user-processes=true\b",
            "%build must not override the requested session-lifetime policy")

    def test_install_checks_the_generated_logind_default(self):
        install = self.section("install")
        guard = re.search(
            r"^\s*grep -qx '#KillUserProcesses=no' "
            r"%\{buildroot\}/etc/systemd/logind\.conf\s*\|\|\s*\{(.*?)^\}",
            install, re.M | re.S)
        self.assertIsNotNone(
            guard, "%install must check the generated logind.conf default")
        self.assertRegex(guard.group(1), r"\becho\b[^\n]*KillUserProcesses",
                         "the guard must explain the incorrect default")
        self.assertRegex(guard.group(1), r"(?m)^\s*exit 1\s*$",
                         "an incorrect default must fail the package build")


if __name__ == "__main__":
    unittest.main()
