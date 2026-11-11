import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def read(relative):
    with open(REPO_ROOT / relative, encoding="utf-8") as handle:
        return handle.read()


class SystemTrayTest(unittest.TestCase):
    """XEmbed tray works; the SNI draft limitation is documented."""

    def test_panel_ships_the_systray_plugin(self):
        filelist = read("package_specs/xfce4-panel/files/xfce4-panel.filelist")
        self.assertIn("/usr/lib64/xfce4/panel/plugins/libsystray.so", filelist)
        self.assertIn("/usr/share/xfce4/panel/plugins/systray.desktop",
                      filelist)

    def test_default_panel_includes_the_systray_plugin(self):
        spec = read("package_specs/tenko-desktop-config/"
                    "tenko-desktop-config.spec")
        self.assertIn('<property name="plugin-6" type="string" value="systray">',
                      spec)
        self.assertNotIn('value="statusnotifier', spec)

    def test_session_check_covers_the_tray(self):
        script = read("scripts/qemu/fdo_session_check.sh")
        self.assertIn("_NET_SYSTEM_TRAY_S0", script)
        self.assertIn("tray-selection", script)
        self.assertIn("tray-plugin", script)
        self.assertIn("sni-host", script)

    def test_matrix_and_rationale(self):
        matrix = read("docs/freedesktop.md")
        for spec in ("systemtray", "xembed"):
            match = re.search(
                r"^\| `" + spec + r"` \|[^|]*\| ([^|]+?) \|", matrix,
                re.MULTILINE,
            )
            self.assertIsNotNone(match, spec)
            self.assertEqual(match.group(1).strip(), "implemented", spec)
        match = re.search(
            r"^\| `status-notifier-item` \|[^|]*\| ([^|]+?) \|", matrix,
            re.MULTILINE,
        )
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1).strip(), "N/A")
        self.assertIn("StatusNotifierItem", matrix)
        self.assertIn("may not show a tray icon", matrix)


if __name__ == "__main__":
    unittest.main()
