"""Every source can be downloaded, and Go/Rust specs declare their toolchain.

`tenko fetch` downloads each tarball from the URL in a package's `sources`
file and checks its md5.  Go and Rust packages download their modules or
crates during the build, so they also need CA certificates (make-ca).
"""

import pathlib
import re
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "package_specs"
sys.path.insert(0, str(REPO_ROOT / "scripts" / "build"))

import fetch_sources  # noqa: E402

# How a spec shows it builds with each toolchain; the toolchain packages
# build themselves from an installed toolchain.
TOOLCHAINS = {r"(?m)^\s*go (build|run)\b": ("go", {"go"}),
              r"CARGO_HOME=": ("rust", {"rust"})}


class SourcesTest(unittest.TestCase):
    def test_every_source_has_a_url(self):
        for path in sorted(SPECS.glob("*/sources")):
            pkg = path.parent.name
            for md5, url, _ in fetch_sources.parse_sources(str(path)):
                self.assertRegex(url, r"^(https?|ftp)://",
                                 "%s: %s has no download URL" % (pkg, url))
                self.assertRegex(md5, r"^[0-9a-f]{32}$", "%s: bad md5" % pkg)

    def test_go_and_rust_packages_declare_the_toolchain(self):
        for spec in sorted(SPECS.glob("*/*.spec")):
            pkg = spec.parent.name
            text = spec.read_text(encoding="utf-8")
            for prefix, (toolchain, exempt) in TOOLCHAINS.items():
                if not re.search(prefix, text) or pkg in exempt:
                    continue
                self.assertRegex(text, r"(?m)^BuildRequires:\s*%s\b" % toolchain,
                                 pkg)
                self.assertRegex(text, r"(?m)^BuildRequires:\s*make-ca\b", pkg)


if __name__ == "__main__":
    unittest.main()
