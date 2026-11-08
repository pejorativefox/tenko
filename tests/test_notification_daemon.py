"""xfce4-notifyd ships the freedesktop notification service and autostart."""

import configparser
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "package_specs"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "xfce4-notifyd"

SERVICE_PATH = "usr/share/dbus-1/services/org.xfce.xfce4-notifyd.Notifications.service"
AUTOSTART_PATH = "etc/xdg/autostart/xfce4-notifyd.desktop"
SERVICE_FIXTURE = FIXTURES / "org.xfce.xfce4-notifyd.Notifications.service"
AUTOSTART_FIXTURE = FIXTURES / "xfce4-notifyd.desktop"


def read(relative):
    with open(REPO_ROOT / relative, encoding="utf-8") as handle:
        return handle.read()


def built_rpms():
    """Newest xfce4-notifyd RPMs produced by a local build, if any."""
    if not (REPO_ROOT / "build").is_dir():
        return []
    return sorted(
        (REPO_ROOT / "build").glob("**/xfce4-notifyd-0.9.7-*.rpm"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def extract_from_rpm(relative):
    """Return a file shipped in a local xfce4-notifyd RPM, or None."""
    if not (shutil.which("rpm2cpio") and shutil.which("cpio")):
        return None
    for rpm in built_rpms():
        if "lang" in rpm.name:
            continue
        tmp = Path(tempfile.mkdtemp(prefix="xfce4-notifyd-test-"))
        try:
            producer = subprocess.Popen(
                ["rpm2cpio", str(rpm)], stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            subprocess.run(
                ["cpio", "-idm", "--quiet", "./" + relative],
                stdin=producer.stdout, cwd=tmp,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            producer.stdout.close()
            producer.wait()
            path = tmp / relative
            if path.is_file():
                return path.read_text(encoding="utf-8")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return None


class NotificationDaemonTest(unittest.TestCase):
    """The package carries a working Desktop Notifications D-Bus service."""

    def shipped_or_fixture(self, relative, fixture):
        text = extract_from_rpm(relative)
        if text is not None:
            return text
        return fixture.read_text(encoding="utf-8")

    def service_text(self):
        return self.shipped_or_fixture(SERVICE_PATH, SERVICE_FIXTURE)

    def autostart_text(self):
        return self.shipped_or_fixture(AUTOSTART_PATH, AUTOSTART_FIXTURE)

    def test_spec_and_sources_track_the_stable_release(self):
        spec = read("package_specs/xfce4-notifyd/xfce4-notifyd.spec")
        self.assertRegex(spec, r"(?m)^Version:\s+0\.9\.7$")
        self.assertRegex(spec, r"(?m)^Release:\s+1$")
        self.assertRegex(spec, r"(?m)^Source0:\s+%\{name\}-%\{version\}\.tar\.bz2$")
        self.assertIn("--disable-wayland", spec)
        self.assertIn("--disable-sound", spec)
        self.assertIn("--disable-systemd", spec)
        self.assertIn(
            "%files -f %{_sourcedir}/xfce4-notifyd.filelist", spec)
        self.assertIn(
            "%files lang -f %{_sourcedir}/xfce4-notifyd-lang.filelist", spec)

        sources = read("package_specs/xfce4-notifyd/sources")
        self.assertIn(
            "https://archive.xfce.org/src/apps/xfce4-notifyd/0.9/"
            "xfce4-notifyd-0.9.7.tar.bz2", sources)
        self.assertRegex(sources, r"(?m)^[0-9a-f]{32} .*xfce4-notifyd-0\.9\.7")

    def test_filelists_ship_the_service_and_autostart_entry(self):
        filelist = read("package_specs/xfce4-notifyd/files/"
                        "xfce4-notifyd.filelist")
        self.assertIn("/" + SERVICE_PATH, filelist)
        self.assertIn("/usr/share/dbus-1/services/"
                      "org.xfce.xfce4-notifyd.Notifyd.service", filelist)
        self.assertIn("/" + AUTOSTART_PATH, filelist)
        self.assertIn("/usr/lib64/xfce4/notifyd/xfce4-notifyd", filelist)
        self.assertIn("/usr/share/applications/xfce4-notifyd-config.desktop",
                      filelist)

        lang = read("package_specs/xfce4-notifyd/files/"
                    "xfce4-notifyd-lang.filelist")
        self.assertIn("/usr/share/locale/de/LC_MESSAGES/xfce4-notifyd.mo",
                      lang)

    def test_static_filelists_use_no_globs(self):
        for name in ("xfce4-notifyd", "xfce4-notifyd-lang"):
            filelist = read("package_specs/xfce4-notifyd/files/"
                            "%s.filelist" % name)
            for line in filelist.splitlines():
                path = line.split(None, 1)[-1]
                self.assertNotIn("*", path, "%s: %s" % (name, line))

    def test_dbus_service_owns_org_freedesktop_notifications(self):
        parser = configparser.ConfigParser(strict=False, interpolation=None)
        parser.read_string(self.service_text())
        self.assertEqual(
            parser.get("D-BUS Service", "Name"),
            "org.freedesktop.Notifications")
        self.assertIn(
            "/usr/lib64/xfce4/notifyd/xfce4-notifyd",
            parser.get("D-BUS Service", "Exec"))

    def test_autostart_entry_starts_the_daemon_in_xfce(self):
        parser = configparser.ConfigParser(strict=False, interpolation=None)
        parser.read_string(self.autostart_text())
        self.assertEqual(parser.get("Desktop Entry", "Type"), "Application")
        only_show_in = [
            item for item in
            parser.get("Desktop Entry", "OnlyShowIn").split(";") if item
        ]
        self.assertIn("XFCE", only_show_in)
        self.assertIn("xfce4-notifyd",
                      parser.get("Desktop Entry", "Exec"))
        self.assertEqual(parser.get("Desktop Entry", "Icon"),
                         "org.xfce.notification")

    @unittest.skipUnless(shutil.which("desktop-file-validate"),
                         "desktop-file-validate not installed")
    def test_autostart_entry_validates(self):
        directory = Path(tempfile.mkdtemp(prefix="xfce4-notifyd-desktop-"))
        try:
            entry = directory / "xfce4-notifyd.desktop"
            entry.write_text(self.autostart_text(), encoding="utf-8")
            result = subprocess.run(
                ["desktop-file-validate", str(entry)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0,
                             result.stdout + result.stderr)
        finally:
            shutil.rmtree(directory, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
