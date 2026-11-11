"""Log evidence parsing in scripts/build/builddeps.py (issue #58)."""

import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts", "build"))

import builddeps  # noqa: E402

LOG = """\
checking for XSETROOT... no
configure: error: Package requirements (xmuu x11) were not met:
Package 'xmuu' not found
Package 'xproto', required by 'virtual:world', not found
No package 'gtk+-3.0' found
Run-time dependency libsystemd found: NO (tried pkgconfig)
ERROR: Dependency "wayland-client" not found, tried pkgconfig
Program gperf found: NO
../meson.build:633:9: ERROR: Program 'xsltproc' not found or not executable
  Could not find a package configuration file provided by "Qt6Core" with
  Could NOT find PNG (missing: PNG_LIBRARY)
/bin/sh: line 1: xsltproc: command not found
/usr/bin/env: 'python2': No such file or directory
Can't locate XML/Parser.pm in @INC (you may need to install the XML::Parser module)
ModuleNotFoundError: No module named 'mako'
../meson.build:832:9: ERROR: Command `/usr/bin/python3 -c 'import jinja2; print(jinja2.__version__)'` failed
"""


class LogCapsTest(unittest.TestCase):
    def test_patterns(self):
        with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as handle:
            handle.write(LOG)
        self.addCleanup(os.unlink, handle.name)
        caps, hints = builddeps.log_caps(handle.name)
        for cap in ("pkgconfig(xmuu)", "pkgconfig(xproto)", "pkgconfig(gtk+-3.0)",
                    "pkgconfig(libsystemd)", "pkgconfig(wayland-client)",
                    "cmake(Qt6Core)", "pkgconfig(png)", "/usr/bin/xsltproc",
                    "/usr/bin/python2", "perl(XML::Parser)", "/usr/bin/gperf"):
            self.assertIn(cap, caps)
        self.assertIn("meson (optional)", caps["pkgconfig(libsystemd)"])
        self.assertIn("python-mako", caps)
        self.assertIn("python-jinja", caps)
        self.assertTrue(any(h.startswith("configure: Package requirements")
                            for h in hints))


if __name__ == "__main__":
    unittest.main()
