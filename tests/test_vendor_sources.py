"""Every source can be downloaded or regenerated (issue #59).

rpmbuild runs offline, so a spec's tarballs must come from a URL in its
`sources` file.  Bundles Tenko generates itself (vendored Rust/Go
dependencies) are hosted under $PUBLIC_URL/sources/<pkg>/ and must carry a
`vendor` marker that `tenko vendor` can regenerate them from.
"""

import os
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "package_specs"
sys.path.insert(0, str(REPO_ROOT / "scripts" / "build"))

import fetch_sources  # noqa: E402
import vendor  # noqa: E402

HOSTED = vendor.PUBLIC_URL + "/sources/"


def all_sources():
    for path in sorted(SPECS.glob("*/sources")):
        for entry in fetch_sources.parse_sources(str(path)):
            yield path.parent.name, entry


class VendorSourcesTest(unittest.TestCase):
    def test_every_source_has_a_url(self):
        for pkg, (md5, url, _) in all_sources():
            self.assertRegex(url, r"^(https?|ftp)://",
                             "%s: %s has no download URL" % (pkg, url))
            self.assertRegex(md5, r"^[0-9a-f]{32}$", "%s: bad md5" % pkg)

    def test_hosted_sources_are_regenerable(self):
        for pkg, (_, url, _) in all_sources():
            if not url.startswith(HOSTED):
                continue
            self.assertTrue(url.startswith(HOSTED + pkg + "/"),
                            "%s: hosted source in another package's directory: %s"
                            % (pkg, url))
            self.assertTrue((SPECS / pkg / "vendor").is_file(),
                            "%s: hosted source without a vendor marker" % pkg)

    def test_vendor_markers(self):
        markers = vendor.marked_packages()
        self.assertTrue(markers)
        for pkg in markers:
            marker = vendor.read_marker(pkg)
            sources = fetch_sources.parse_sources(str(SPECS / pkg / "sources"))
            names = {fetch_sources.source_filename(s) for s in sources}
            for key in ("tree", "lockfile"):
                if key in marker:
                    self.assertIn(marker[key], names, "%s: %s" % (pkg, key))
            hosted = [s for s in sources if s[1].startswith(HOSTED + pkg + "/")]
            self.assertEqual(len(hosted), 1,
                             "%s: expected one hosted vendor bundle" % pkg)
            self.assertTrue(hosted[0][1].endswith("-vendor.tar.xz"), pkg)
            spec = (SPECS / pkg / (pkg + ".spec")).read_text(encoding="utf-8")
            self.assertIn("-vendor.tar.xz", spec, pkg)

    def test_go_packages_declare_the_toolchain(self):
        for pkg in vendor.marked_packages():
            kind = vendor.read_marker(pkg)["kind"]
            spec = (SPECS / pkg / (pkg + ".spec")).read_text(encoding="utf-8")
            wanted = "BuildRequires: go" if kind == "go" else "BuildRequires: rust"
            self.assertIn(wanted, spec, pkg)


if __name__ == "__main__":
    unittest.main()
