"""tenko-sysconfig must not statically enable serial-getty@ttyS0.

systemd-getty-generator starts serial-getty@ttyS0 from console=ttyS0 on the
kernel command line, which the live ISO and the QEMU tests pass.  A static
getty.target.wants symlink only adds a getty that fails and restarts every
10 seconds on hardware without a serial port.  The package removes the link
left by older releases from %posttrans.
"""

import os
import re
import unittest

from specutil import read_spec

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(
    REPO_ROOT, "package_specs", "tenko-sysconfig", "tenko-sysconfig.spec")
ISO = os.path.join(REPO_ROOT, "scripts", "image", "iso.sh")
QEMU = os.path.join(REPO_ROOT, "scripts", "lib", "qemu.sh")

LINK = "/etc/systemd/system/getty.target.wants/serial-getty@ttyS0.service"
UNIT = "/usr/lib/systemd/system/serial-getty@ttyS0.service"


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def section(spec, name):
    match = re.search(r"(?ms)^%" + name + r"\s*\n(.*?)(?=^%[a-z])", spec)
    if not match:
        raise AssertionError("tenko-sysconfig has no %" + name + " section")
    return match.group(1)


class SerialGettyTest(unittest.TestCase):
    def test_install_does_not_enable_serial_getty(self):
        install = section(read_spec(SPEC), "install")
        self.assertNotIn("serial-getty", install)
        self.assertNotIn("getty.target.wants", install)

    def test_filelist_does_not_own_the_stale_link(self):
        spec = read_spec(SPEC)
        self.assertNotIn("%config(noreplace) " + LINK, spec)

    def test_posttrans_removes_only_the_old_link(self):
        posttrans = section(read_spec(SPEC), "posttrans")
        self.assertIn(LINK, posttrans)
        self.assertIn('readlink "$link"', posttrans)
        self.assertIn(UNIT, posttrans)
        self.assertIn("console=ttyS0", posttrans)
        self.assertIn('rm -f "$link"', posttrans)
        self.assertIn("systemctl daemon-reload", posttrans)
        # A user-written unit or override must not be removed.
        self.assertNotIn("rm -f /etc/systemd/system/serial-getty@ttyS0.service",
                         posttrans)

    def test_serial_console_still_comes_from_the_kernel_command_line(self):
        self.assertIn("console=ttyS0", read(ISO))
        self.assertIn("console=ttyS0", read(QEMU))


if __name__ == "__main__":
    unittest.main()
