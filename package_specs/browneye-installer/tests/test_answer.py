import os
import sys
import tempfile
import unittest

FILES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files")
sys.path.insert(0, FILES)

import main  # noqa: E402


class AnswerPathTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "answer.json")
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("{}")

    def test_explicit_existing(self):
        self.assertEqual(main.find_answer_path(self.path, timeout=0), self.path)

    def test_missing_returns_none_after_timeout(self):
        self.assertIsNone(main.find_answer_path(
            os.path.join(self.tmp.name, "nope.json"), timeout=0))

    def test_mount_answer_disk_without_medium(self):
        if os.path.exists(main.ANSWER_LABEL):
            self.skipTest("a BROWNEYE-ANSWER medium is present")
        self.assertIsNone(main.mount_answer_disk())

    def test_search_list(self):
        old = main.ANSWER_PATHS
        main.ANSWER_PATHS = (self.path,)
        self.addCleanup(setattr, main, "ANSWER_PATHS", old)
        self.assertEqual(main.find_answer_path(None, timeout=0), self.path)


if __name__ == "__main__":
    unittest.main()
