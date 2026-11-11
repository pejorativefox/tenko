import re
import unittest
from pathlib import Path

from specutil import expand_if_spec as _expand_spec

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "package_specs"


def read(relative):
    with open(REPO_ROOT / relative, encoding="utf-8") as handle:
        return _expand_spec(handle.read(), REPO_ROOT / relative)


class PolkitAgentTest(unittest.TestCase):
    """A polkit agent starts with the session and wheel can authenticate."""

    def test_xfce_polkit_is_packaged(self):
        spec = read("package_specs/xfce-polkit/xfce-polkit.spec")
        sources = read("package_specs/xfce-polkit/sources")
        self.assertIn("Version:    0.3", spec)
        self.assertIn("Requires:   polkit", spec)
        self.assertIn("/etc/xdg/autostart/xfce-polkit.desktop", spec)
        self.assertIn("/usr/libexec/xfce-polkit", spec)
        self.assertIn("xfce-polkit-0.3.tar.gz", sources)

    def test_agent_is_in_the_desktop_profiles(self):
        for name in ("xfce-desktop", "xfce-desktop-core"):
            spec = read("package_specs/%s/%s.spec" % (name, name))
            self.assertIn("Requires:   xfce-polkit", spec, name)

    def test_wheel_is_the_polkit_administrator(self):
        spec = read("package_specs/tenko-sysconfig/tenko-sysconfig.spec")
        match = re.search(
            r"cat > %%\{buildroot\}%s <<'EOF2'\n(.*?)\nEOF2"
            % re.escape("/etc/polkit-1/rules.d/50-tenko-wheel.rules"),
            spec, re.S,
        )
        self.assertIsNotNone(match)
        self.assertIn("polkit.addAdminRule", match.group(1))
        self.assertIn("unix-group:wheel", match.group(1))
        self.assertIn(
            "%config(noreplace) /etc/polkit-1/rules.d/50-tenko-wheel.rules",
            spec,
        )
        installer = read("package_specs/tenko-installer/files/install.py")
        self.assertIn("wheel", installer)

    def test_polkit_daemon_and_tools_are_shipped(self):
        filelist = read("package_specs/polkit/files/polkit.filelist")
        for path in (
            "/usr/bin/pkexec",
            "/usr/lib/polkit-1/polkitd",
            "/usr/share/dbus-1/system.d/org.freedesktop.PolicyKit1.conf",
            "/usr/share/polkit-1/actions/org.freedesktop.policykit.policy",
        ):
            self.assertIn(path, filelist)

    def test_autostart_entry_is_shipped_by_upstream(self):
        tarball = Path.home() / "rpmbuild" / "SOURCES" / "xfce-polkit-0.3.tar.gz"
        if not tarball.is_file():
            self.skipTest("xfce-polkit source tarball is not staged")
        import tarfile
        with tarfile.open(tarball) as archive:
            member = archive.extractfile("xfce-polkit-0.3/xfce-polkit.desktop.in")
            self.assertIsNotNone(member)
            text = member.read().decode("utf-8")
        self.assertIn("Exec=@xfce_polkit_libexecdir@/xfce-polkit", text)
        self.assertIn("NotShowIn=GNOME;KDE;", text)


if __name__ == "__main__":
    unittest.main()
