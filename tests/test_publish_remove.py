"""tenko publish remove drops a package's entries from all metadata."""

import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts/publish/remove_packages.py"

PRIMARY = """<?xml version="1.0" encoding="UTF-8"?>
<metadata xmlns="http://linux.duke.edu/metadata/common" xmlns:rpm="http://linux.duke.edu/metadata/rpm" packages="3">
<package type="rpm">
  <name>go</name>
  <checksum type="sha256" pkgid="YES">aaa</checksum>
  <location href="go-2-1.x86_64.rpm"/>
  <format>
    <rpm:provides>
      <rpm:entry name="go-bin" flags="EQ" ver="2"/>
    </rpm:provides>
  </format>
</package>
<package type="rpm">
  <name>go-bin</name>
  <checksum type="sha256" pkgid="YES">bbb</checksum>
  <location href="go-bin-1-1.x86_64.rpm"/>
  <format>
    <rpm:provides>
      <rpm:entry name="go-bin-only"/>
    </rpm:provides>
  </format>
</package>
<package type="rpm">
  <name>gh</name>
  <checksum type="sha256" pkgid="YES">ccc</checksum>
  <location href="gh-1-1.x86_64.rpm"/>
  <format>
    <rpm:requires>
      <rpm:entry name="go-bin"/>
    </rpm:requires>
  </format>
</package>
</metadata>
"""


def side(kind, root):
    return ("""<?xml version="1.0" encoding="UTF-8"?>
<%s xmlns="x" packages="3">
<package pkgid="aaa" name="go" arch="x86_64">
</package>
<package pkgid="bbb" name="go-bin" arch="x86_64">
</package>
<package pkgid="ccc" name="gh" arch="x86_64">
</package>
</%s>
""" % (root, root))


class RemovePackagesTest(unittest.TestCase):
    def run_script(self, primary, *names):
        src = tempfile.mkdtemp()
        dst = os.path.join(src, "out")
        for name, text in (("primary", primary),
                           ("filelists", side("f", "filelists")),
                           ("other", side("o", "otherdata"))):
            with open(os.path.join(src, name + ".xml"), "w") as handle:
                handle.write(text)
        result = subprocess.run([sys.executable, str(SCRIPT), src, dst, *names],
                                capture_output=True, text=True)
        return result, dst

    def test_removes_entries_everywhere(self):
        result, dst = self.run_script(PRIMARY, "go-bin")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.split(), ["go-bin-1-1.x86_64.rpm"])
        for name in ("primary", "filelists", "other"):
            text = pathlib.Path(dst, name + ".xml").read_text()
            self.assertNotIn("bbb", text, name)
            self.assertIn('packages="2"', text, name)
            self.assertIn("aaa", text, name)

    def test_refuses_to_break_a_dependency(self):
        broken = PRIMARY.replace('<rpm:entry name="go-bin"/>',
                                 '<rpm:entry name="go-bin-only"/>')
        result, _ = self.run_script(broken, "go-bin")
        self.assertEqual(result.returncode, 1)
        self.assertIn("gh (requires go-bin-only)", result.stderr)

    def test_refuses_unknown_names(self):
        result, _ = self.run_script(PRIMARY, "nope")
        self.assertEqual(result.returncode, 1)
        self.assertIn("nope", result.stderr)


if __name__ == "__main__":
    unittest.main()
