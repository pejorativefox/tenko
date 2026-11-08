import configparser
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


def section(text, marker):
    """Return the body of a spec section (for example %post)."""
    match = re.search(
        r"^" + re.escape(marker) + r"(?: [^\n]*)?\n(.*?)(?=^%[a-zA-Z])",
        text, re.S | re.MULTILINE,
    )
    return match.group(1) if match else ""


def trigger(text, path, command):
    normalised = (
        text.replace("%{_datadir}", "/usr/share")
        .replace("%{_sysconfdir}", "/etc")
        .replace("%{_prefix}", "/usr")
    )
    for match in re.finditer(
        r"^%transfiletrigger(?:in|postun) -- (\S+)\n(.*?)(?=^%|\Z)",
        normalised, re.S | re.MULTILINE,
    ):
        if match.group(1).rstrip("/") == path and command in match.group(2):
            return True
    return False


def shipped_desktop_ids():
    ids = set()
    for path in SPECS.glob("*/files/*.filelist"):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.search(r"/applications/([^/\s]+\.desktop)$", line)
            if match:
                ids.add(match.group(1))
    for path in SPECS.glob("*/*.spec"):
        for line in path.read_text(encoding="utf-8").splitlines():
            installed = line.strip().replace("%{buildroot}", "")
            installed = installed.replace("%{_datadir}", "/usr/share")
            match = re.search(r"/applications/([^/\s]+\.desktop)$", installed)
            if match:
                ids.add(match.group(1))
    return ids


class DesktopMetadataTest(unittest.TestCase):
    """XDG desktop metadata is self-maintaining and has working defaults."""

    def test_database_triggers_are_installed(self):
        self.assertTrue(
            trigger(spec_text("desktop-file-utils"),
                    "/usr/share/applications", "update-desktop-database"))
        self.assertTrue(
            trigger(spec_text("shared-mime-info"),
                    "/usr/share/mime", "update-mime-database"))
        self.assertTrue(
            trigger(spec_text("gtk3"),
                    "/usr/share/icons", "gtk-update-icon-cache"))

    def test_no_ad_hoc_cache_calls_remain(self):
        for name in ("mpv", "firefox-bin", "google-chrome-bin", "kora-icon-theme"):
            text = spec_text(name)
            for marker in ("%post", "%postun"):
                body = section(text, marker)
                self.assertNotIn("update-desktop-database", body, name)
                self.assertNotIn("gtk-update-icon-cache", body, name)
                self.assertNotIn("update-mime-database", body, name)

    def test_icon_themes_inherit_only_hicolor(self):
        adwaita = spec_text("adwaita-icon-theme")
        self.assertIn("sed -i 's/^Inherits=.*/Inherits=hicolor/'", adwaita)
        kora = spec_text("kora-icon-theme")
        self.assertIn("sed -i 's/^Inherits=.*/Inherits=hicolor/'", kora)
        self.assertIn("kora kora-pgrey", kora)

    def test_desktop_profiles_install_the_metadata_tools(self):
        for name in ("xfce-desktop", "xfce-desktop-core"):
            text = spec_text(name)
            self.assertIn("Requires:   xdg-utils", text, name)
            self.assertIn("Requires:   desktop-file-utils", text, name)
        self.assertIn("Requires:   mpv", spec_text("xfce-desktop-core"))

    def test_default_mimeapps_file_is_complete(self):
        text = read("package_specs/tenko-desktop-config/files/mimeapps.list")
        parser = configparser.ConfigParser(strict=False, interpolation=None)
        parser.read_string(text)
        defaults = parser["Default Applications"]
        for mime in ("text/plain", "image/png", "inode/directory",
                     "x-scheme-handler/http", "x-scheme-handler/help"):
            self.assertIn(mime, defaults)
        self.assertTrue(any(key.startswith("audio/") for key in defaults))
        self.assertTrue(any(key.startswith("video/") for key in defaults))
        shipped = shipped_desktop_ids()
        for mime, value in defaults.items():
            for desktop_id in (item.strip() for item in value.split(";")):
                if desktop_id:
                    self.assertIn(desktop_id, shipped,
                                  "%s points at %s" % (mime, desktop_id))

    def test_help_layout_and_handler_are_installed(self):
        spec = spec_text("tenko-desktop-config")
        self.assertIn("%{_datadir}/help/tenko/index.html", spec)
        self.assertIn("%{_datadir}/help/C/tenko/index.html", spec)
        self.assertIn("tenko-help.desktop", spec)
        self.assertIn("Requires:   xdg-utils", spec)
        script = read("package_specs/tenko-desktop-config/files/tenko-help")
        self.assertIn("help:*)", script)
        self.assertIn("/usr/share/help/C/tenko/index.html", script)
        self.assertIn("printf '%s\\n' \"$page\"", script)
        self.assertTrue(
            os.access(REPO_ROOT / "package_specs/tenko-desktop-config/files/tenko-help",
                      os.X_OK)
        )

    @unittest.skipUnless(shutil.which("desktop-file-validate"),
                         "desktop-file-validate not installed")
    def test_new_desktop_entry_validates(self):
        for name in ("tenko-help.desktop", "xfce-graphical-session.desktop"):
            entry = (REPO_ROOT / "package_specs/tenko-desktop-config/files/"
                     / name)
            result = subprocess.run(
                ["desktop-file-validate", str(entry)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0,
                             name + ": " + result.stdout + result.stderr)

    def test_help_script_resolves_an_installed_page(self):
        script = REPO_ROOT / "package_specs/tenko-desktop-config/files/tenko-help"
        result = subprocess.run(
            ["sh", "-n", str(script)], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
