"""Guard the cups %pre user/group setup.

A fresh ``dnf --installroot`` transaction can pull cups in through
``libcups.so.2`` (google-chrome-bin) before systemd's sysusers run has
created the lp group.  The %pre scriptlet must therefore create the group
itself before ``useradd -g lp``, or the whole transaction fails with
"group 'lp' does not exist".
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(REPO_ROOT, "package_specs", "cups", "cups.spec")


def read_spec():
    with open(SPEC, encoding="utf-8") as handle:
        return handle.read()


def pre_section(spec):
    match = re.search(r"(?ms)^%pre\s*\n(.*?)(?=^%[a-z])", spec)
    if not match:
        raise AssertionError("cups spec has no %pre section")
    return match.group(1)


class CupsScriptletTest(unittest.TestCase):
    def test_pre_requires_shadow(self):
        self.assertRegex(read_spec(), r"(?m)^Requires\(pre\):\s+shadow\s*$")

    def test_pre_creates_lp_group_before_useradd(self):
        pre = pre_section(read_spec())
        create_lp = pre.find("groupadd -g 9 lp")
        create_lpadmin = pre.find("groupadd -g 19 lpadmin")
        useradd = pre.find("useradd ")
        self.assertGreaterEqual(create_lp, 0,
                                "%pre must create the lp group (gid 9)")
        self.assertGreaterEqual(create_lpadmin, 0,
                                "%pre must create the lpadmin group (gid 19)")
        self.assertGreaterEqual(useradd, 0, "%pre must create the lp user")
        self.assertLess(create_lp, useradd,
                        "create the lp group before useradd -g lp")
        self.assertLess(create_lpadmin, useradd)
        self.assertIn("getent group lp >/dev/null ||", pre)
        self.assertIn("-g lp", pre[useradd:])


if __name__ == "__main__":
    unittest.main()
