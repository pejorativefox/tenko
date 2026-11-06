import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, "scripts", "gen_repo_index.py")


class GenRepoIndexTest(unittest.TestCase):
    def render(self, listing):
        workdir = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(workdir))
        src = os.path.join(workdir, "files.txt")
        out = os.path.join(workdir, "index.html")
        with open(src, "w", encoding="utf-8") as handle:
            handle.write(listing)
        subprocess.run(
            [sys.executable, SCRIPT, src, out, "6",
             "https://example.org/tenko/packages/6/", "tenko-6"],
            check=True, capture_output=True, text=True)
        with open(out, encoding="utf-8") as handle:
            return handle.read()

    def test_lists_only_rpm_files(self):
        page = self.render(
            "htop-3.5.3-1.x86_64.rpm 207681\n"
            "repomd.xml 1234\n"
            "bash-5.3-2.x86_64.rpm 705882\n")
        self.assertIn("htop-3.5.3-1.x86_64.rpm", page)
        self.assertIn("bash-5.3-2.x86_64.rpm", page)
        self.assertNotIn("repomd.xml", page)
        self.assertIn("2 RPMs", page)
        self.assertIn("tenko-6.repo", page)

    def test_escapes_names_and_sorts(self):
        page = self.render(
            "z-1-1.x86_64.rpm 1048576\n"
            "a&amp;-1-1.noarch.rpm 1\n")
        self.assertLess(page.index("a&amp;amp;-1-1.noarch.rpm"),
                        page.index("z-1-1.x86_64.rpm"))
        self.assertIn("1.0 MB", page)

    def test_empty_listing(self):
        page = self.render("")
        self.assertIn("0 RPMs", page)


if __name__ == "__main__":
    unittest.main()
