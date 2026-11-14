import os
import re
import shutil
import subprocess
import tempfile
import time
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


def processes_using(home):
    """PIDs of our processes with a file under home open or mapped."""
    prefix = str(home) + "/"
    pids = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            targets = [os.readlink(fd) for fd in (entry / "fd").iterdir()]
            maps = (entry / "maps").read_text(encoding="utf-8",
                                              errors="replace")
        except OSError:
            continue
        if (any(t.startswith(prefix) for t in targets)
                or prefix in maps):
            pids.append(int(entry.name))
    return pids


GIO_TRASH = shutil.which("gio") and shutil.which("dbus-run-session")


class TrashThumbnailTest(unittest.TestCase):
    """Trash, Recent Files and Thumbnail Managing Standard integration."""

    def setUp(self):
        # The home trash must be on the same filesystem as the trashed file
        # and /tmp is often tmpfs, so the fake home lives under the real one.
        self.home = Path(tempfile.mkdtemp(prefix="trash-home-", dir=Path.home()))
        self.addCleanup(self.remove_home)
        self.env = os.environ.copy()
        self.env["HOME"] = str(self.home)
        self.env["XDG_DATA_HOME"] = str(self.home / ".local" / "share")
        self.env["XDG_CACHE_HOME"] = str(self.home / ".cache")

    def gio_trash(self, path):
        # gio derives the metadata journal path from its own XDG_DATA_HOME
        # and hands it to gvfsd-metadata over D-Bus.  On the user's session
        # bus that is the long-running daemon, which keeps the journal open
        # and recreates the fake home when it rotates it (issue #65).  A
        # private bus gets its own daemon, which exits with the bus.
        return subprocess.run(
            ["dbus-run-session", "--", "gio", "trash", str(path)],
            env=self.env, capture_output=True, text=True,
        )

    def remove_home(self):
        deadline = time.monotonic() + 5
        leaked = processes_using(self.home)
        while leaked and time.monotonic() < deadline:
            time.sleep(0.1)
            leaked = processes_using(self.home)
        shutil.rmtree(self.home, True)
        self.assertEqual(leaked, [], "processes still use the test home: %s" % leaked)
        self.assertFalse(self.home.exists())

    @unittest.skipUnless(GIO_TRASH, "gio or dbus-run-session not installed")
    def test_gio_trash_creates_home_trash_layout(self):
        source = self.home / "trashme.txt"
        source.write_text("trash me\n", encoding="utf-8")
        result = self.gio_trash(source)
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

    @unittest.skipUnless(GIO_TRASH, "gio or dbus-run-session not installed")
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
        result = self.gio_trash(source)
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
