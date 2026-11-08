import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "package_specs"
METAINFO = SPECS / "tenko-release" / "files" / "org.tenko.Tenko.metainfo.xml"


def read(relative):
    with open(REPO_ROOT / relative, encoding="utf-8") as handle:
        return handle.read()


def spec_text(name):
    return read("package_specs/%s/%s.spec" % (name, name))


class AppstreamTest(unittest.TestCase):
    """AppStream metadata is installed, valid and searchable on the desktop."""

    def test_distro_component_is_shipped(self):
        spec = spec_text("tenko-release")
        self.assertTrue(METAINFO.is_file())
        self.assertIn(
            "org.tenko.Tenko.metainfo.xml", spec)
        self.assertIn(
            "%{_datadir}/metainfo/org.tenko.Tenko.metainfo.xml", spec)

    def test_distro_component_has_the_required_fields(self):
        root = ET.parse(METAINFO).getroot()
        self.assertEqual(root.tag, "component")
        self.assertEqual(root.get("type"), "operating-system")
        values = {child.tag: (child.text or "").strip() for child in root}
        self.assertEqual(values.get("id"), "org.tenko.Tenko")
        self.assertEqual(values.get("name"), "Tenko Linux")
        self.assertTrue(values.get("summary"))
        self.assertTrue(values.get("metadata_license"))
        self.assertTrue(values.get("project_license"))

    def test_desktop_profiles_install_appstream(self):
        for name in ("xfce-desktop", "xfce-desktop-core"):
            self.assertIn("Requires:   appstream", spec_text(name), name)
        filelist = read("package_specs/appstream/files/appstream.filelist")
        self.assertIn("/usr/bin/appstreamcli", filelist)

    def test_chrome_error_is_waived(self):
        matrix = read("docs/freedesktop.md")
        self.assertIn("google-chrome.appdata.xml", matrix)
        self.assertIn("type-property-required", matrix)
        self.assertIn("#42", matrix)

    @unittest.skipUnless(shutil.which("appstreamcli"),
                         "appstreamcli not installed")
    def test_distro_component_validates(self):
        result = subprocess.run(
            ["appstreamcli", "validate", "--no-net", str(METAINFO)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("E:", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
