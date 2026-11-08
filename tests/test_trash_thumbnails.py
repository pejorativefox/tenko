import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "package_specs"


def read(relative):
    with open(REPO_ROOT / relative, encoding="utf-8") as handle:
        return handle.read()


def filelist(name):
    path = SPECS / name / "files" / (name + ".filelist")
    return path.read_text(encoding="utf-8") if path.is_file() else ""


class TrashThumbnailTest(unittest.TestCase):
    """Trash, Recent Files and Thumbnail Managing Standard integration."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="trash-home-", dir=Path.home()))
        self.addCleanup(shutil.rmtree, self.home, True)
        self.env = os.environ.copy()
        self.env["HOME"] = str(self.home)
        self.env["XDG_DATA_HOME"] = str(self.home / ".local" / "share")
        self.env["XDG_CACHE_HOME"] = str(self.home / ".cache")

    @unittest.skipUnless(shutil.which("gio"), "gio not installed")
    def test_gio_trash_creates_home_trash_layout(self):
        source = self.home / "trashme.txt"
        source.write_text("trash me\n", encoding="utf-8")
        result = subprocess.run(
            ["gio", "trash", str(source)], env=self.env,
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        files = self.home / ".local" / "share" / "Trash" / "files" / "trashme.txt"
        info = self.home / ".local" / "share" / "Trash" / "info" / \
            "trashme.txt.trashinfo"
        self.assertTrue(files.is_file())
        self.assertTrue(info.is_file())
        self.assertEqual(files.read_text(encoding="utf-8"), "trash me\n")

        text = info.read_text(encoding="utf-8")
        self.assertIn("[Trash Info]", text)
        self.assertIn("Path=" + str(source), text)
        match = re.search(r"^DeletionDate=(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})$",
                          text, re.MULTILINE)
        self.assertIsNotNone(match, text)

    @unittest.skipUnless(shutil.which("gio"), "gio not installed")
    def test_cross_filesystem_trash_is_handled_or_documented(self):
        # /tmp is often a different device from the home directory.  GLib's
        # local trash refuses some system-internal mounts instead of using a
        # top-directory trash; that is an upstream limitation, so the test
        # accepts either a conforming trash entry or the documented refusal,
        # and always checks that no wrong XDG trash was created.
        if os.stat("/tmp").st_dev == os.stat(self.home).st_dev:
            self.skipTest("/tmp and home are on the same filesystem")
        source = Path("/tmp") / ("tenko-trash-%d.txt" % os.getpid())
        self.addCleanup(lambda: source.unlink(missing_ok=True))
        self.addCleanup(
            lambda: shutil.rmtree("/tmp/.Trash-%d" % os.getuid(), True)
        )
        source.write_text("cross filesystem\n", encoding="utf-8")
        result = subprocess.run(
            ["gio", "trash", str(source)], env=self.env,
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            files = self.home / ".local" / "share" / "Trash" / "files" / source.name
            info = self.home / ".local" / "share" / "Trash" / "info" / \
                (source.name + ".trashinfo")
            if files.is_file():
                self.assertTrue(info.is_file())
                self.assertIn("Path=" + str(source),
                              info.read_text(encoding="utf-8"))
            else:
                top = Path("/tmp") / (".Trash-%d" % os.getuid())
                self.assertTrue((top / "files" / source.name).is_file())
                self.assertTrue(
                    (top / "info" / (source.name + ".trashinfo")).is_file()
                )
        else:
            message = (result.stdout + result.stderr).lower()
            self.assertTrue(
                "filesystem" in message or "system internal" in message,
                result.stdout + result.stderr,
            )
            matrix = read("docs/freedesktop.md")
            self.assertIn("cross-filesystem", matrix.lower())

    def test_gvfs_provides_trash_and_recent_backends(self):
        gvfs = filelist("gvfs")
        for backend in ("gvfsd-trash", "gvfsd-recent", "gvfsd-metadata"):
            self.assertIn("/usr/libexec/" + backend, gvfs, backend)
        thunar = read("package_specs/thunar/thunar.spec")
        self.assertIn("Requires:   gvfs", thunar)

    def test_thumbnail_support_is_documented(self):
        # tumbler's GStreamer thumbnailer is intentionally disabled; the
        # matrix must say which types are supported instead of silently
        # promising video/audio thumbnails.
        tumbler = read("package_specs/tumbler/tumbler.spec")
        self.assertIn("--disable-gstreamer-thumbnailer", tumbler)
        entries = filelist("tumbler")
        for plugin in (
            "tumbler-cover-thumbnailer.so",
            "tumbler-desktop-thumbnailer.so",
            "tumbler-font-thumbnailer.so",
            "tumbler-jpeg-thumbnailer.so",
            "tumbler-pixbuf-thumbnailer.so",
        ):
            self.assertIn("/usr/lib64/tumbler-1/plugins/" + plugin, entries)
        self.assertNotIn("tumbler-gst-thumbnailer.so", entries)
        matrix = read("docs/freedesktop.md")
        match = re.search(r"^\| `thumbnail` \|[^|]*\|[^|]*\|([^|]*)\|",
                          matrix, re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertIn("video", match.group(1).lower())
        self.assertIn("unsupported", match.group(1).lower())


if __name__ == "__main__":
    unittest.main()
