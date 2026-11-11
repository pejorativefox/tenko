import hashlib
import os
import pathlib
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts", "build"))

import fetch_sources  # noqa: E402


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
        self.assertEqual(fetch_sources.parse_sources(path), [
            ["abc", "https://example.org/foo.tar.gz", None],
            ["def", "https://example.org/bar.tar.gz", "bar-local.tar.gz"],
        ])

    def test_mangled_line_raises(self):
        path = self.write("only-one-field\n")
        with self.assertRaises(ValueError):
            fetch_sources.parse_sources(path)


class FetchSourcesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = os.path.join(self.tmp.name, "source-file")
        pathlib.Path(self.source).write_bytes(b"hello tenko\n")
        self.md5 = hashlib.md5(b"hello tenko\n").hexdigest()
        self.dest = os.path.join(self.tmp.name, "SOURCES")

    def item(self, md5=None, name="cached.tar.gz"):
        return [md5 or self.md5, pathlib.Path(self.source).as_uri(), name]

    def test_download_and_cached(self):
        self.assertTrue(fetch_sources.fetch_sources(
            [self.item()], self.dest, jobs=1))
        target = os.path.join(self.dest, "cached.tar.gz")
        self.assertTrue(os.path.isfile(target))
        self.assertFalse(os.path.exists(target + ".part"))
        # Second call must hit the cache and still succeed.
        self.assertTrue(fetch_sources.fetch_sources(
            [self.item()], self.dest, jobs=1))

    def test_corrupt_cache_is_replaced(self):
        os.makedirs(self.dest)
        target = os.path.join(self.dest, "cached.tar.gz")
        pathlib.Path(target).write_bytes(b"stale")
        self.assertTrue(fetch_sources.fetch_sources(
            [self.item()], self.dest, jobs=1))
        self.assertEqual(fetch_sources.get_md5(target), self.md5)

    def test_bad_md5_leaves_nothing_behind(self):
        self.assertFalse(fetch_sources.fetch_sources(
            [self.item(md5="0" * 32)], self.dest, jobs=1))
        target = os.path.join(self.dest, "cached.tar.gz")
        self.assertFalse(os.path.exists(target))
        self.assertFalse(os.path.exists(target + ".part"))


class ResolvePackageDirTest(unittest.TestCase):
    def test_spec_path_relative_to_package_specs(self):
        self.assertEqual(
            fetch_sources.resolve_package_dir("curl/curl.spec"),
            os.path.join(REPO_ROOT, "package_specs", "curl"))

    def test_bare_package_name(self):
        self.assertEqual(
            fetch_sources.resolve_package_dir("curl"),
            os.path.join(REPO_ROOT, "package_specs", "curl"))

    def test_unknown_name(self):
        self.assertIsNone(fetch_sources.resolve_package_dir("not-a-package"))


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dest = os.path.join(self.tmp.name, "SOURCES")

    def make_package(self, name, sources=None, nosources=False):
        path = os.path.join(self.tmp.name, name)
        os.makedirs(path)
        pathlib.Path(os.path.join(path, name + ".spec")).write_text("")
        if sources is not None:
            pathlib.Path(os.path.join(path, "sources")).write_text(sources)
        if nosources:
            pathlib.Path(os.path.join(path, "nosources")).write_text("")
        return path

    def test_fetches_listed_sources(self):
        source = os.path.join(self.tmp.name, "blob.tar.gz")
        pathlib.Path(source).write_bytes(b"blob\n")
        md5 = hashlib.md5(b"blob\n").hexdigest()
        package = self.make_package(
            "demo", "{0} {1} blob.tar.gz\n".format(
                md5, pathlib.Path(source).as_uri()))
        rc = fetch_sources.main(["--dest", self.dest, package])
        self.assertEqual(rc, 0)
        self.assertEqual(
            fetch_sources.get_md5(os.path.join(self.dest, "blob.tar.gz")),
            md5)

    def test_nosources_is_skipped(self):
        package = self.make_package("meta", nosources=True)
        rc = fetch_sources.main(["--dest", self.dest, package])
        self.assertEqual(rc, 0)
        self.assertFalse(os.path.isdir(self.dest))

    def test_missing_sources_file_is_skipped(self):
        package = self.make_package("empty")
        rc = fetch_sources.main(["--dest", self.dest, package])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()


class SeedAndStageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(__import__("shutil").rmtree, self.tmp)

    def test_seeded_from_old_cache_without_download(self):
        seed = self.tmp / "seed"
        dest = self.tmp / "dest"
        seed.mkdir()
        (seed / "foo.tar.gz").write_bytes(b"payload")
        md5 = hashlib.md5(b"payload").hexdigest()
        old = fetch_sources.SEED_DIRS
        fetch_sources.SEED_DIRS = [str(seed)]
        self.addCleanup(setattr, fetch_sources, "SEED_DIRS", old)
        # An unreachable URL proves nothing was downloaded.
        ok = fetch_sources._fetch_one(
            [md5, "http://127.0.0.1:9/foo.tar.gz", None], str(dest))
        self.assertTrue(ok)
        self.assertEqual((dest / "foo.tar.gz").read_bytes(), b"payload")

    def test_stage_links_only_the_packages_own_files(self):
        pkg = self.tmp / "specs" / "foo"
        other = self.tmp / "specs" / "bar"
        sources = self.tmp / "sources"
        for d in (pkg / "files", other / "files", sources):
            d.mkdir(parents=True)
        (pkg / "foo.spec").write_text("Name: foo\n")
        (pkg / "files" / "foo.filelist").write_text("/usr/bin/foo\n")
        (other / "files" / "bar.patch").write_text("patch\n")
        (pkg / "sources").write_text(
            "abc https://example.org/dl/download foo-1.tar.gz\n")
        (sources / "foo-1.tar.gz").write_bytes(b"tarball")
        (sources / "bar-1.tar.gz").write_bytes(b"other")
        root = self.tmp / "out"
        spec = str(pkg / "foo.spec")
        fetch_sources.stage([spec], [str(pkg)], str(sources), str(root))
        staged = sorted(os.listdir(root / "foo" / "SOURCES"))
        self.assertEqual(staged, ["foo-1.tar.gz", "foo.filelist"])
