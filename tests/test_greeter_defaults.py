import configparser
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE = "lightdm-gtk-greeter"
SPECS = REPO_ROOT / "package_specs" / PACKAGE
CONF = SPECS / "files" / "lightdm-gtk-greeter.conf"
KORA_FILELIST = (REPO_ROOT / "package_specs" / "kora-icon-theme" / "files"
                 / "kora-icon-theme.filelist")

# Icons the greeter asks the theme for.  The symbolic variants are preferred;
# hicolor does not ship them, which is what left the indicator buttons blank.
GREETER_ICONS = (
    "preferences-desktop-accessibility-symbolic",
    "system-shutdown-symbolic",
    "document-properties-symbolic",
    "view-refresh-symbolic",
    "avatar-default",
)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def greeter_config():
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(read(CONF))
    return parser["greeter"]


class GreeterDefaultsTest(unittest.TestCase):
    """The login screen matches the desktop theme and has working icons."""

    def test_login_screen_uses_a_black_background(self):
        greeter = greeter_config()
        self.assertEqual(greeter["background"], "#000000")
        # A per-user background image would hide the black backdrop.
        self.assertEqual(greeter["user-background"], "false")

    def test_login_screen_uses_arc_dark_and_kora(self):
        greeter = greeter_config()
        self.assertEqual(greeter["theme-name"], "Arc-Dark")
        self.assertEqual(greeter["icon-theme-name"], "kora")

    def test_config_replaces_the_upstream_template(self):
        spec = read(SPECS / "lightdm-gtk-greeter.spec")
        self.assertIn("Source1:    lightdm-gtk-greeter.conf", spec)
        self.assertIn(
            "install -Dpm0644 %{SOURCE1} "
            "%{buildroot}%{_sysconfdir}/lightdm/lightdm-gtk-greeter.conf",
            spec)
        self.assertIn(
            "%config(noreplace) /etc/lightdm/lightdm-gtk-greeter.conf",
            read(SPECS / "files" / "lightdm-gtk-greeter.filelist"))

    def test_the_named_theme_packages_are_required(self):
        spec = read(SPECS / "lightdm-gtk-greeter.spec")
        self.assertIn("Requires: arc-theme", spec)
        self.assertIn("Requires: kora-icon-theme", spec)

    def test_kora_provides_the_greeter_icons(self):
        icons = read(KORA_FILELIST)
        for icon in GREETER_ICONS:
            self.assertIn("/%s" % icon, icons, icon)


if __name__ == "__main__":
    unittest.main()
