import os
import re
import unittest

from specutil import expand_if_spec as _expand_spec

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")

DROPIN = "/etc/systemd/logind.conf.d/10-lid-switch.conf"
PATCH = ("xfce4-power-manager/files/"
         "xfce4-power-manager-4.20.1-logind-lid-switch.patch")


def read(relative):
    with open(os.path.join(SPECS, relative), encoding="utf-8") as handle:
        return _expand_spec(handle.read(), os.path.join(SPECS, relative))


class LidSwitchPolicyTest(unittest.TestCase):
    """Lid handling is logind policy, not a desktop setting.

    A power manager that claims handle-lid-switch stops logind from applying
    HandleLidSwitch at all, so both halves have to stay in place: the drop-in
    with the policy, and the power manager default that leaves the switch to
    logind.
    """

    def test_logind_dropin_is_packaged(self):
        text = read("tenko-sysconfig/tenko-sysconfig.spec")
        self.assertIn("/etc/systemd/logind.conf.d", text)
        self.assertIn("%dir /etc/systemd/logind.conf.d", text)
        self.assertIn("%config(noreplace) " + DROPIN, text)

    def test_logind_dropin_has_the_lid_policy(self):
        text = read("tenko-sysconfig/tenko-sysconfig.spec")
        match = re.search(
            r"cat > %\{buildroot\}" + re.escape(DROPIN) +
            r" <<'EOF2'\n(.*?)\nEOF2", text, re.S)
        self.assertIsNotNone(match, "spec does not write " + DROPIN)
        lines = match.group(1).splitlines()
        self.assertIn("[Login]", lines)
        self.assertIn("HandleLidSwitch=suspend", lines)
        self.assertIn("HandleLidSwitchExternalPower=suspend", lines)
        self.assertIn("HandleLidSwitchDocked=ignore", lines)

    def test_power_manager_does_not_claim_the_lid_switch(self):
        spec = read("xfce4-power-manager/xfce4-power-manager.spec")
        self.assertIn("Patch0:", spec)
        self.assertIn("%patch -P 0 -p1", spec)
        patch = read(PATCH)
        self.assertIn("-#define DEFAULT_LOGIND_HANDLE_LID_SWITCH FALSE", patch)
        self.assertIn("+#define DEFAULT_LOGIND_HANDLE_LID_SWITCH TRUE", patch)


if __name__ == "__main__":
    unittest.main()
