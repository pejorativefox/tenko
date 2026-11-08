import configparser
import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "package_specs" / "sound-theme-freedesktop"

PACKAGE = "sound-theme-freedesktop"
VERSION = "0.8"
RELEASE = "1"
SOURCE_MD5 = "91c3c4bf2e6abb704661a9c28a4c655d"
SOURCE_URL = (
    "https://gitlab.freedesktop.org/xdg/xdg-sound-theme/-/archive/0.8/"
    "xdg-sound-theme-0.8.tar.gz"
)
THEME_DIR = "/usr/share/sounds/freedesktop"

# Event names from Sound Naming 0.2 that the theme must resolve.  libcanberra
# looks these up verbatim, so a missing file means a silent event.
REQUIRED_EVENTS = (
    "bell",
    "complete",
    "device-added",
    "device-removed",
    "dialog-error",
    "dialog-information",
    "dialog-warning",
    "message",
    "service-login",
    "service-logout",
    "suspend-error",
    "trash-empty",
    "audio-volume-change",
)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def filelist():
    return read(SPECS / "files" / ("%s.filelist" % PACKAGE)).splitlines()


def parse_theme(text):
    parser = configparser.ConfigParser(strict=False, interpolation=None)
    parser.read_string(text)
    return parser


def find_rpm():
    candidates = sorted(
        (REPO_ROOT / "build").glob("**/%s-*.noarch.rpm" % PACKAGE),
        key=lambda path: path.stat().st_mtime,
    )
    return candidates[-1] if candidates else None


def rpm_files(rpm):
    out = subprocess.check_output(["rpm", "-qlp", str(rpm)], text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]


def rpm_extract(rpm, member):
    """Return the contents of one file from an RPM, or None if unavailable."""
    if shutil.which("rpm2cpio") is None or shutil.which("cpio") is None:
        return None
    archive = subprocess.check_output(["rpm2cpio", str(rpm)])
    result = subprocess.run(
        ["cpio", "-i", "--to-stdout", member],
        input=archive, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8")


class SoundThemeTest(unittest.TestCase):
    """The freedesktop sound theme is complete enough for libcanberra."""

    def test_spec_tracks_stable_version(self):
        spec = read(SPECS / ("%s.spec" % PACKAGE))
        self.assertIn("Version:    %s" % VERSION, spec)
        self.assertIn("Release:    %s" % RELEASE, spec)
        self.assertIn("BuildArch:  noarch", spec)
        self.assertIn("Source0:    %{name}-%{version}.tar.gz", spec)
        self.assertIn("sound-theme-freedesktop", spec.split("%changelog", 1)[1])

    def test_sources_record_the_archive(self):
        lines = [line for line in read(SPECS / "sources").splitlines() if line]
        self.assertEqual(len(lines), 1)
        md5, url, filename = lines[0].split()
        self.assertEqual(md5, SOURCE_MD5)
        self.assertEqual(url, SOURCE_URL)
        self.assertEqual(filename, "%s-%s.tar.gz" % (PACKAGE, VERSION))

    def test_static_filelist_installs_the_theme(self):
        entries = filelist()
        self.assertIn(THEME_DIR + "/index.theme", entries)
        self.assertEqual(entries.count("%dir " + THEME_DIR + "/stereo"), 1)
        sounds = [entry for entry in entries if entry.endswith(".oga")]
        self.assertGreaterEqual(len(sounds), 30)
        for event in REQUIRED_EVENTS:
            self.assertIn("%s/stereo/%s.oga" % (THEME_DIR, event), entries,
                          event)

    def test_index_theme_has_the_sound_theme_group(self):
        theme = parse_theme(read(SPECS / "files" / "index.theme"))
        self.assertIn("Sound Theme", theme)
        section = theme["Sound Theme"]
        self.assertEqual(section.get("Directories"), "stereo")
        # The Sound Theme spec names a theme after its directory; libcanberra
        # resolves the fallback theme as /usr/share/sounds/freedesktop.
        self.assertEqual(Path(THEME_DIR).name, "freedesktop")
        self.assertEqual(section.get("Name"), "freedesktop")
        self.assertEqual(theme["stereo"].get("OutputProfile"), "stereo")

    def test_missing_theme_falls_back_to_freedesktop(self):
        # libcanberra (src/sound-theme-spec.c) uses "freedesktop" for both
        # DEFAULT_THEME and FALLBACK_THEME: if the configured theme is
        # missing it retries this directory.  Shipping index.theme there is
        # what makes that fallback resolve instead of failing silently.
        entries = filelist()
        self.assertIn(THEME_DIR + "/index.theme", entries)
        self.assertIn(THEME_DIR + "/stereo/bell.oga", entries)

    def test_built_rpm_contains_index_theme_and_events(self):
        rpm = find_rpm()
        if rpm is None:
            self.skipTest("no built %s RPM under build/" % PACKAGE)
        if shutil.which("rpm") is None:
            self.skipTest("rpm is not installed")
        installed = rpm_files(rpm)
        self.assertIn(THEME_DIR + "/index.theme", installed)
        for event in REQUIRED_EVENTS:
            self.assertIn("%s/stereo/%s.oga" % (THEME_DIR, event), installed,
                          event)
        # The package must own the whole theme, not just a few samples.
        packaged = {path for path in installed
                    if path.startswith(THEME_DIR + "/stereo/")
                    and path.endswith(".oga")}
        for entry in filelist():
            if entry.endswith(".oga"):
                self.assertIn(entry, packaged)
        extracted = rpm_extract(rpm, "." + THEME_DIR + "/index.theme")
        if extracted is None:
            self.skipTest("rpm2cpio/cpio unavailable to extract index.theme")
        theme = parse_theme(extracted)
        self.assertIn("Sound Theme", theme)
        self.assertEqual(theme["Sound Theme"].get("Directories"), "stereo")
        self.assertEqual(theme["Sound Theme"].get("Name"), "freedesktop")


if __name__ == "__main__":
    unittest.main()
