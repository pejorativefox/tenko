import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "package_specs"


def read(relative):
    with open(REPO_ROOT / relative, encoding="utf-8") as handle:
        return handle.read()


def spec_text(name):
    return read("package_specs/%s/%s.spec" % (name, name))


class PortalTest(unittest.TestCase):
    """The portal, its GTK backend and Flatpak are default desktop parts."""

    def test_portal_and_backend_are_packaged(self):
        portal = spec_text("xdg-desktop-portal")
        backend = spec_text("xdg-desktop-portal-gtk")
        self.assertIn("Version:    1.22.1", portal)
        self.assertIn("Version:    1.15.3", backend)
        self.assertIn("Requires:   xdg-desktop-portal", backend)
        self.assertIn(
            "/usr/share/xdg-desktop-portal/portals/gtk.portal",
            read("package_specs/xdg-desktop-portal-gtk/files/"
                 "xdg-desktop-portal-gtk.filelist"),
        )
        self.assertIn("org.freedesktop.portal.Desktop.service", portal)

    def test_desktop_profiles_install_the_portal_stack(self):
        for name in ("xfce-desktop", "xfce-desktop-core"):
            spec = spec_text(name)
            for package in ("flatpak", "xdg-desktop-portal",
                            "xdg-desktop-portal-gtk"):
                self.assertIn("Requires:   " + package, spec, name)

    def test_xfce_portals_conf_selects_gtk(self):
        spec = spec_text("xfce4-session")
        match = re.search(
            r"cat > %\{buildroot\}%\{_datadir\}/xdg-desktop-portal/"
            r"xfce-portals\.conf <<'EOF'\n(.*?)\nEOF", spec, re.S,
        )
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1).strip(), "[preferred]\ndefault=gtk;")
        self.assertNotIn("xapp", match.group(1))
        self.assertIn("/usr/share/xdg-desktop-portal/xfce-portals.conf",
                      read("package_specs/xfce4-session/files/xfce4-session.filelist"))

    def test_flatpak_remotes_and_policy_are_shipped(self):
        spec = spec_text("flatpak")
        self.assertIn("flathub.flatpakrepo", spec)
        self.assertIn("50-tenko-flatpak.rules", spec)
        self.assertTrue((SPECS / "flatpak" / "files" /
                         "flathub.flatpakrepo").is_file())
        self.assertTrue((SPECS / "flatpak" / "files" /
                         "50-tenko-flatpak.rules").is_file())

    def test_gtk_backend_advertises_the_supported_interfaces(self):
        rpms = sorted(
            (REPO_ROOT / "build").glob("**/xdg-desktop-portal-gtk-*.rpm"),
            key=lambda path: path.stat().st_mtime,
        )
        if not rpms or not shutil.which("rpm2cpio") or not shutil.which("cpio"):
            self.skipTest("no built xdg-desktop-portal-gtk RPM")
        archive = subprocess.check_output(["rpm2cpio", str(rpms[-1])])
        result = subprocess.run(
            ["cpio", "-i", "--to-stdout",
             "./usr/share/xdg-desktop-portal/portals/gtk.portal"],
            input=archive, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            self.skipTest("gtk.portal is not in the built RPM")
        text = result.stdout.decode("utf-8")
        for interface in (
            "FileChooser", "AppChooser", "Print", "Notification", "Inhibit",
            "Access", "Account", "Email", "DynamicLauncher", "Lockdown",
            "Settings",
        ):
            self.assertIn("org.freedesktop.impl.portal." + interface, text)


if __name__ == "__main__":
    unittest.main()
