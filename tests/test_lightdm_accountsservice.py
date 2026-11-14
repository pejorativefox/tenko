import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "package_specs" / "lightdm"
INTERFACE = "org.freedesktop.DisplayManager.AccountsService.xml"


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


class LightdmAccountsServiceTest(unittest.TestCase):
    """accounts-daemon must see lightdm's extension interface (issue #57)."""

    def test_spec_keeps_the_interface_symlink(self):
        spec = read(SPECS / "lightdm.spec")
        self.assertNotIn("rm -rf %{buildroot}%{_datadir}/accountsservice", spec)

    def test_spec_requires_accountsservice(self):
        spec = read(SPECS / "lightdm.spec")
        self.assertRegex(spec, r"(?m)^Requires:\s+accountsservice\s*$")

    def test_filelist_ships_symlink_and_its_target(self):
        filelist = read(SPECS / "files" / "lightdm.filelist").splitlines()
        self.assertIn("/usr/share/accountsservice/interfaces/" + INTERFACE,
                      filelist)
        self.assertIn("/usr/share/dbus-1/interfaces/" + INTERFACE, filelist)
        # accountsservice owns the directory.
        self.assertNotIn("%dir /usr/share/accountsservice/interfaces",
                         filelist)


if __name__ == "__main__":
    unittest.main()
