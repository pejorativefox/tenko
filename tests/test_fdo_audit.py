import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check" / "fdo_audit.py"
REAL_DOC = REPO_ROOT / "docs" / "freedesktop.md"
SPEC_INDEX = (
    "appstream",
    "autostart",
    "basedir",
    "clipboard",
    "clipboard-extensions",
    "dbus",
    "desktop-entry",
    "fhs",
    "global-shortcuts",
    "help-system",
    "icon-naming",
    "icon-theme",
    "idle-inhibit",
    "intent-apps",
    "menu",
    "mime-apps",
    "mpris",
    "notification",
    "polkit",
    "recent-files",
    "secret-service",
    "shortcuts",
    "shared-mime-info",
    "sound-naming",
    "sound-theme",
    "startup-notification",
    "status-notifier-item",
    "systemtray",
    "terminal-intent",
    "thumbnail",
    "trash",
    "wm",
    "xembed",
    "xsettings",
    "XDG user dirs",
    "xdg-desktop-portal",
)


def run_audit(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


class FdoAuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fdo-audit-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    # -- fixture helpers -------------------------------------------------
    def matrix(self, **changes):
        text = REAL_DOC.read_text(encoding="utf-8")
        for spec, disposition in changes.items():
            pattern = re.compile(
                r"^(\| `" + re.escape(spec) + r"` \|[^|]*\| )([^|]+?)( \|)",
                re.MULTILINE,
            )
            text, count = pattern.subn(
                lambda match: match.group(1) + disposition + match.group(3),
                text,
                count=1,
            )
            self.assertEqual(count, 1, f"matrix row {spec!r} not found")
        path = self.tmp / "freedesktop.md"
        path.write_text(text, encoding="utf-8")
        return path

    def write(self, relative, content):
        path = self.tmp / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def specs(self, triggers=True):
        profile = "Requires:   desktop-file-utils\nRequires:   xdg-utils\n"
        self.write("specs/xfce-desktop/xfce-desktop.spec", profile)
        if triggers:
            self.write(
                "specs/desktop-file-utils/desktop-file-utils.spec",
                "%transfiletriggerin -- /usr/share/applications\n"
                "update-desktop-database /usr/share/applications || :\n",
            )
            self.write(
                "specs/shared-mime-info/shared-mime-info.spec",
                "%transfiletriggerin -- /usr/share/mime\n"
                "update-mime-database /usr/share/mime || :\n",
            )
            self.write(
                "specs/icon-theme/icon-theme.spec",
                "%transfiletriggerin -- /usr/share/icons\n"
                "gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || :\n",
            )
        return self.tmp / "specs"

    def root(self, icon=True, desktop=None):
        root = self.tmp / "root"
        apps = root / "usr" / "share" / "applications"
        apps.mkdir(parents=True)
        if desktop is None:
            desktop = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=Good\n"
                "Exec=/usr/bin/good\n"
                "Icon=good\n"
                "Categories=Utility;\n"
            )
        (apps / "good.desktop").write_text(desktop, encoding="utf-8")
        hicolor = root / "usr" / "share" / "icons" / "hicolor"
        hicolor.mkdir(parents=True)
        (hicolor / "index.theme").write_text(
            "[Icon Theme]\nName=Hicolor\nInherits=\n", encoding="utf-8"
        )
        if icon:
            icon_dir = hicolor / "48x48" / "apps"
            icon_dir.mkdir(parents=True)
            (icon_dir / "good.png").write_bytes(b"\x89PNG\r\n")
        return root

    # -- matrix guardrail ------------------------------------------------
    def test_real_matrix_lists_every_spec(self):
        result = run_audit("--no-rpm", "--only", "docs")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"{len(SPEC_INDEX)}/{len(SPEC_INDEX)} matrix rows", result.stdout)

    def test_missing_matrix_row_fails(self):
        doc = self.tmp / "freedesktop.md"
        text = REAL_DOC.read_text(encoding="utf-8")
        text = re.sub(r"^\| `wm` .*$\n", "", text, count=1, flags=re.MULTILINE)
        doc.write_text(text, encoding="utf-8")
        result = run_audit("--no-rpm", "--only", "docs", "--doc", str(doc))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("missing spec row 'wm'", result.stdout)

    def test_partial_row_without_issue_fails(self):
        text = REAL_DOC.read_text(encoding="utf-8")
        text = text.replace(
            "| `mpris` | current spec | N/A | Application responsibility "
            "(media players); no distro service |",
            "| `mpris` | current spec | partial | no owner |",
        )
        doc = self.tmp / "freedesktop.md"
        doc.write_text(text, encoding="utf-8")
        result = run_audit("--no-rpm", "--only", "docs", "--doc", str(doc))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("partial row has no linked issue", result.stdout)

    # -- desktop metadata ------------------------------------------------
    def test_broken_desktop_entry_fails_when_implemented(self):
        doc = self.matrix(**{"desktop-entry": "implemented"})
        specs = self.specs()
        root = self.root(desktop="this is not a desktop file\n")
        result = run_audit(
            "--root", str(root), "--only", "desktop-entry",
            "--doc", str(doc), "--spec-root", str(specs),
        )
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("error", result.stdout.lower())

    def test_missing_icon_fails_when_implemented(self):
        doc = self.matrix(**{"icon-naming": "implemented"})
        specs = self.specs(triggers=False)
        root = self.root(icon=False)
        result = run_audit(
            "--root", str(root), "--only", "icon-naming",
            "--doc", str(doc), "--spec-root", str(specs),
        )
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("does not resolve", result.stdout)

    def test_missing_database_trigger_fails(self):
        doc = self.matrix(**{"desktop-entry": "implemented"})
        specs = self.specs(triggers=False)
        root = self.root()
        result = run_audit(
            "--root", str(root), "--only", "desktop-entry",
            "--doc", str(doc), "--spec-root", str(specs),
        )
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("missing update-desktop-database file trigger", result.stdout)

    def test_valid_fixture_passes(self):
        doc = self.matrix(
            **{"desktop-entry": "implemented", "icon-naming": "implemented"}
        )
        specs = self.specs()
        root = self.root()
        result = run_audit(
            "--root", str(root), "--only", "desktop-entry,icon-naming",
            "--doc", str(doc), "--spec-root", str(specs),
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PASS  desktop-entry", result.stdout)
        self.assertIn("PASS  icon-naming", result.stdout)

    def test_missing_mimeapps_fails_when_implemented(self):
        doc = self.matrix(**{"mime-apps": "implemented"})
        specs = self.specs(triggers=False)
        root = self.root()
        result = run_audit(
            "--root", str(root), "--only", "mime-apps",
            "--doc", str(doc), "--spec-root", str(specs),
        )
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("no default mimeapps.list", result.stdout)

    @unittest.skipUnless(shutil.which("appstreamcli"), "appstreamcli not installed")
    def test_invalid_appstream_fails_when_implemented(self):
        doc = self.matrix(**{"appstream": "implemented"})
        specs = self.specs(triggers=False)
        root = self.root()
        metainfo = self.tmp / "root" / "usr" / "share" / "metainfo"
        metainfo.mkdir(parents=True)
        (metainfo / "org.example.Bad.metainfo.xml").write_text(
            "<component type='desktop-application'></component>\n", encoding="utf-8"
        )
        result = run_audit(
            "--root", str(root), "--only", "appstream",
            "--doc", str(doc), "--spec-root", str(specs),
        )
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("appstreamcli", result.stdout)

    def test_reports_one_line_per_matrix_row(self):
        result = run_audit("--no-rpm")
        for spec in SPEC_INDEX:
            self.assertIn(spec, result.stdout, f"no result line for {spec!r}")
        self.assertIn("36/36 matrix rows", result.stdout)


if __name__ == "__main__":
    unittest.main()
