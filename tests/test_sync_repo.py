"""scripts/build/sync_repo.py against a hand-built file:// repository."""

import gzip
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "build" / "sync_repo.py"

REPOMD = """<?xml version="1.0" encoding="UTF-8"?>
<repomd xmlns="http://linux.duke.edu/metadata/repo">
  <data type="primary">
    <checksum type="sha256">{sum}</checksum>
    <location href="repodata/{name}"/>
  </data>
</repomd>
"""
PACKAGE = """<package type="rpm">
  <name>{name}</name><arch>noarch</arch>
  <checksum type="sha256" pkgid="YES">{sum}</checksum>
  <size package="{size}" installed="0" archive="0"/>
  <location href="{name}-1-1.noarch.rpm"/>
</package>"""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


class SyncRepoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.upstream = self.tmp / "upstream"
        self.dest = self.tmp / "mirror"

    def publish(self, packages):
        shutil.rmtree(self.upstream, ignore_errors=True)
        (self.upstream / "repodata").mkdir(parents=True)
        entries = []
        for name, payload in packages.items():
            (self.upstream / "{}-1-1.noarch.rpm".format(name)).write_bytes(payload)
            entries.append(PACKAGE.format(name=name, sum=sha256(payload),
                                          size=len(payload)))
        primary = gzip.compress((
            '<metadata xmlns="http://linux.duke.edu/metadata/common" '
            'packages="{}">{}</metadata>'.format(len(entries), "".join(entries))
        ).encode())
        name = sha256(primary) + "-primary.xml.gz"
        (self.upstream / "repodata" / name).write_bytes(primary)
        (self.upstream / "repodata" / "repomd.xml").write_text(
            REPOMD.format(sum=sha256(primary), name=name))

    def sync(self, *urls):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--dest", str(self.dest), *urls],
            capture_output=True, text=True)

    def url(self):
        return self.upstream.as_uri() + "/"

    def test_mirrors_updates_and_prunes(self):
        self.publish({"foo": b"foo-1", "bar": b"bar-1"})
        result = self.sync(self.url())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sorted(p.name for p in self.dest.glob("*.rpm")),
                         ["bar-1-1.noarch.rpm", "foo-1-1.noarch.rpm"])

        result = self.sync(self.url())
        self.assertIn("mirror is current", result.stdout)

        self.publish({"foo": b"foo-1", "baz": b"baz-1"})
        result = self.sync(self.url())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 downloaded, 1 removed", result.stdout)
        self.assertEqual(sorted(p.name for p in self.dest.glob("*.rpm")),
                         ["baz-1-1.noarch.rpm", "foo-1-1.noarch.rpm"])

    def test_first_reachable_url_wins_and_offline_keeps_mirror(self):
        self.publish({"foo": b"foo-1"})
        dead = (self.tmp / "missing").as_uri() + "/"
        result = self.sync(dead, self.url())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.dest / "foo-1-1.noarch.rpm").is_file())
        result = self.sync(dead)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("using the existing mirror", result.stdout)

    def test_bad_checksum_keeps_old_metadata(self):
        self.publish({"foo": b"foo-1"})
        self.assertEqual(self.sync(self.url()).returncode, 0)
        before = (self.dest / "repodata" / "repomd.xml").read_bytes()
        self.publish({"foo": b"foo-1", "bar": b"bar-1"})
        (self.upstream / "bar-1-1.noarch.rpm").write_bytes(b"corrupt")
        result = self.sync(self.url())
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.dest / "repodata" / "repomd.xml").read_bytes(),
                         before)


if __name__ == "__main__":
    unittest.main()
