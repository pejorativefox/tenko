import os
import subprocess
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")
PKG = os.path.join(SPECS, "tenko-suspend-log")
FILES = os.path.join(PKG, "files")

SCRIPTS = ("50-tenko-suspend-log", "tenko-resume-probe",
           "tenko-suspend-check", "tenko-suspend-report")


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as handle:
        return handle.read()


def script(name):
    return read(FILES, name)


class SuspendLogTest(unittest.TestCase):
    """Every cycle gets a start, a resume and a user-space probe marker.

    The probe marker is what lets tenko-suspend-check tell a completed resume
    from a machine that hung after action=start.
    """

    def test_scripts_are_valid_bash(self):
        for name in SCRIPTS:
            subprocess.run(["bash", "-n", os.path.join(FILES, name)],
                           check=True)

    def test_sleep_hook_logs_both_phases(self):
        hook = script("50-tenko-suspend-log")
        self.assertIn("action=start", hook)
        self.assertIn("action=resume", hook)
        self.assertIn("logger -t", hook)
        self.assertIn("systemctl start --no-block tenko-resume-probe", hook)
        self.assertIn("/etc/tenko/suspend-debug", hook)
        self.assertIn("pm_debug_messages", hook)

    def test_probe_is_the_completion_marker(self):
        probe = script("tenko-resume-probe")
        self.assertIn("action=probe", probe)
        self.assertIn("xset q", probe)
        self.assertIn("dpms force on", probe)

    def test_boot_check_warns_about_unfinished_cycles(self):
        check = script("tenko-suspend-check")
        self.assertIn("action=start", check)
        self.assertIn("action=probe", check)
        self.assertIn("did not complete", check)

    def test_report_collects_the_suspend_state(self):
        report = script("tenko-suspend-report")
        for needle in ("suspend_stats", "/proc/acpi/wakeup", "Xorg.0.log",
                       "dmesg", "pstore", "journalctl", "suspend.txt"):
            self.assertIn(needle, report)
        self.assertIn("fwupdmgr", report)

    def test_spec_installs_and_enables_the_units(self):
        spec = read(PKG, "tenko-suspend-log.spec")
        for path in (
                "/usr/lib/systemd/system-sleep/50-tenko-suspend-log",
                "/usr/libexec/tenko/tenko-resume-probe",
                "/usr/libexec/tenko/tenko-suspend-check",
                "/usr/lib/systemd/system/tenko-suspend-check.service",
                "/usr/lib/systemd/system/tenko-resume-probe.service",
                "/usr/lib/systemd/system-preset/40-tenko-suspend-log.preset"):
            self.assertIn(path, spec)
        self.assertIn("systemctl preset tenko-suspend-check.service", spec)
        preset = script("40-tenko-suspend-log.preset")
        self.assertIn("enable tenko-suspend-check.service", preset)

    def test_package_is_in_the_base_install(self):
        extras = read(SPECS, "tenko-base", "requires-extra")
        self.assertIn("tenko-suspend-log", extras.split())
        self.assertIn("Requires:   tenko-suspend-log",
                      read(SPECS, "tenko-base", "tenko-base.spec"))


if __name__ == "__main__":
    unittest.main()
