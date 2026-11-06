import hashlib
import os
import pathlib
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "builder"))

import db  # noqa: E402
import package as pkg  # noqa: E402
import sources  # noqa: E402
from build import spec_nevra  # noqa: E402


class ParseSourcesTest(unittest.TestCase):
    def write(self, text):
        handle = tempfile.NamedTemporaryFile("w", delete=False)
        handle.write(text)
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def test_two_and_three_fields_and_comments(self):
        path = self.write(
            "# comment\n"
            "\n"
            "abc https://example.org/foo.tar.gz\n"
            "def https://example.org/bar.tar.gz bar-local.tar.gz\n")
        self.assertEqual(sources.parse_sources(path), [
            ["abc", "https://example.org/foo.tar.gz", None],
            ["def", "https://example.org/bar.tar.gz", "bar-local.tar.gz"],
        ])

    def test_mangled_line_raises(self):
        path = self.write("only-one-field\n")
        with self.assertRaises(ValueError):
            sources.parse_sources(path)


class FetchSourcesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old_sources_dir = sources.SOURCES_DIR
        sources.SOURCES_DIR = self.tmp.name
        self.addCleanup(setattr, sources, "SOURCES_DIR", self.old_sources_dir)

    def test_download_and_cached(self):
        source = os.path.join(self.tmp.name, "source-file")
        pathlib.Path(source).write_bytes(b"hello tenko\n")
        md5 = hashlib.md5(b"hello tenko\n").hexdigest()
        item = [md5, pathlib.Path(source).as_uri(), "cached.tar.gz"]
        self.assertTrue(sources._fetch_one(item))
        target = os.path.join(self.tmp.name, "cached.tar.gz")
        self.assertTrue(os.path.isfile(target))
        self.assertFalse(os.path.exists(target + ".part"))
        # Second call must hit the cache.
        self.assertTrue(sources._fetch_one(item))

    def test_corrupt_cache_is_replaced(self):
        source = os.path.join(self.tmp.name, "source-file")
        pathlib.Path(source).write_bytes(b"payload\n")
        md5 = hashlib.md5(b"payload\n").hexdigest()
        item = [md5, pathlib.Path(source).as_uri(), "cached.tar.gz"]
        target = os.path.join(self.tmp.name, "cached.tar.gz")
        pathlib.Path(target).write_bytes(b"stale")
        self.assertTrue(sources._fetch_one(item))
        self.assertEqual(hashlib.md5(open(target, "rb").read()).hexdigest(), md5)


class ResolveTest(unittest.TestCase):
    def test_alias_and_missing(self):
        packages = {"pcre2": object(), "zlib": object()}
        self.assertEqual(pkg.resolve_package_name("pcre2", packages), "pcre2")
        self.assertEqual(
            pkg.resolve_package_name("pcre", packages, {"pcre": "pcre2"}),
            "pcre2")
        self.assertIsNone(pkg.resolve_package_name("nope", packages))

    def test_load_order_ignores_comments(self):
        handle = tempfile.NamedTemporaryFile("w", delete=False)
        handle.write("a # comment\n\nb\n")
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        self.assertEqual(pkg.load_order(handle.name), ["a", "b"])


class NevraTest(unittest.TestCase):
    def test_spec_nevra(self):
        nevra = spec_nevra(os.path.join(
            REPO_ROOT, "package_specs", "zlib", "zlib.spec"))
        self.assertIsNotNone(nevra)
        self.assertTrue(nevra.startswith("zlib-"))

    def test_missing_spec_returns_none(self):
        self.assertIsNone(spec_nevra("/nonexistent/x.spec"))


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "package.db")

    def test_state_and_read_only(self):
        database = db.PackageDatabase(self.path)
        self.assertTrue(database.add_package("zlib"))
        self.assertFalse(database.add_package("zlib"))
        self.assertFalse(database.is_built("zlib"))
        database.set_built("zlib")
        self.assertTrue(database.is_built("zlib"))
        database.set_failed("zlib")
        self.assertFalse(database.is_built("zlib"))
        database.close()

        ro = db.PackageDatabase.read_only(self.path)
        self.assertEqual([row[1] for row in ro.get_failed()], ["zlib"])
        ro.close()

    def test_read_only_missing_raises(self):
        with self.assertRaises(FileNotFoundError):
            db.PackageDatabase.read_only(self.path)


if __name__ == "__main__":
    unittest.main()
