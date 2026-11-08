import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "package_specs"


def read(relative):
    with open(REPO_ROOT / relative, encoding="utf-8") as handle:
        return handle.read()


def spec_text(name):
    return read("package_specs/%s/%s.spec" % (name, name))


def filelist(name):
    return read("package_specs/%s/files/%s.filelist" % (name, name))


class SecretServiceTest(unittest.TestCase):
    """gnome-keyring provides org.freedesktop.secrets and unlocks at login."""

    def test_gnome_keyring_is_packaged(self):
        spec = spec_text("gnome-keyring")
        sources = read("package_specs/gnome-keyring/sources")
        self.assertIn("Version:    50.0", spec)
        self.assertIn("LGPL-2.1-or-later", spec)
        self.assertIn("gnome-keyring-50.0.tar.xz", sources)
        self.assertIn("-Dpam=true", spec)
        self.assertIn("-Dssh-agent=false", spec)

    def test_secret_service_and_portal_backend_are_shipped(self):
        entries = filelist("gnome-keyring")
        for path in (
            "/usr/share/dbus-1/services/org.freedesktop.secrets.service",
            "/usr/share/dbus-1/services/org.freedesktop.impl.portal.Secret.service",
            "/usr/share/xdg-desktop-portal/portals/gnome-keyring.portal",
            "/usr/lib64/security/pam_gnome_keyring.so",
            "/etc/xdg/autostart/gnome-keyring-secrets.desktop",
        ):
            self.assertIn(path, entries)

    def test_desktop_profiles_install_the_provider(self):
        for name in ("xfce-desktop", "xfce-desktop-core"):
            self.assertIn("Requires:   gnome-keyring", spec_text(name), name)

    def test_lightdm_unlocks_the_login_keyring(self):
        spec = spec_text("lightdm")
        self.assertIn("pam_gnome_keyring.so", spec)
        self.assertIn("auth      optional pam_gnome_keyring.so", spec)
        self.assertIn(
            "session   optional pam_gnome_keyring.so auto_start", spec)
        self.assertIn("Recommends:    gnome-keyring", spec)

    def test_portal_secret_backend_is_selected(self):
        spec = spec_text("xfce4-session")
        self.assertIn(
            "org.freedesktop.impl.portal.Secret=gnome-keyring;", spec)

    def test_secret_tool_is_available(self):
        self.assertIn("/usr/bin/secret-tool", spec_text("libsecret"))

    def test_matrix_marks_secret_service_implemented(self):
        matrix = read("docs/freedesktop.md")
        match = re.search(
            r"^\| `secret-service` \|[^|]*\| ([^|]+?) \|", matrix,
            re.MULTILINE,
        )
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1).strip(), "implemented")


if __name__ == "__main__":
    unittest.main()
