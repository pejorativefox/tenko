import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "package_specs", "browneye-installer", "files"))

import probe  # noqa: E402


class ReadTextTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = self.tmp.name

    def test_regular_file(self):
        path = os.path.join(self.dir, "text")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("hello\n")
        self.assertEqual(probe._read_text(path), "hello\n")

    def test_fifo_is_not_read(self):
        path = os.path.join(self.dir, "fifo")
        os.mkfifo(path)
        # A blocking read would hang the test; the stat check must return "".
        self.assertEqual(probe._read_text(path), "")

    def test_character_device_is_not_read(self):
        self.assertEqual(probe._read_text("/dev/null"), "")

    def test_livedev_symlink_is_resolved_not_read(self):
        if not os.path.exists("/dev/null"):
            self.skipTest("no /dev/null")
        link = os.path.join(self.dir, "livedev")
        os.symlink("/dev/null", link)
        self.assertTrue(os.path.islink(link))
        self.assertEqual(os.path.realpath(link), "/dev/null")


if __name__ == "__main__":
    unittest.main()
