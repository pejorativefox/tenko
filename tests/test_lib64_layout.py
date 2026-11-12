"""Architecture libraries live in /usr/lib64, not /usr/lib.

Autotools/CMake/meson and the hand-written Makefiles default their library
directory to $PREFIX/lib.  Tenko is 64-bit only and builds every package with
/usr/lib64, so a spec that forgets to override the default silently splits
the toolchain.  Consumers then need non-standard pkg-config and loader paths.
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")

# glibc keeps its CRT objects and linker scripts in /usr/lib while the shared
# libraries are installed through libc_cv_slibdir=/usr/lib64.  This is the
# upstream libdir/slibdir split, not a packaging mistake.
TOP_LEVEL_ALLOWED = {"glibc"}

# pm-utils.pc describes the package's own /usr/lib/pm-utils data directory;
# there is no compiled library behind it.
PKGCONFIG_ALLOWED = {"pm-utils"}

LIBDIR_ARGS = {
    "ffmpeg": ("--libdir=%{_libdir}", "--shlibdir=%{_libdir}"),
    "cups": ("--libdir=%{_libdir}", "--with-pkgconfpath=%{_libdir}/pkgconfig"),
    "db": ("--libdir=%{_libdir}",),
    "duktape": ("LIBDIR=/lib64",),
    "giflib": ("LIBDIR=/usr/lib64",),
    "luajit": ("MULTILIB=lib64",),
    "tzdb": ("LIBDIR=%{_libdir}",),
}

TOP_LEVEL_LIB = re.compile(r"^/usr/lib/[^/]+\.(?:so(?:\.[0-9.]+)*|a)$")


def filelists():
    for package in sorted(os.listdir(SPECS)):
        directory = os.path.join(SPECS, package, "files")
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            if name.endswith(".filelist"):
                yield package, os.path.join(directory, name)


def paths(filelist):
    with open(filelist, encoding="utf-8") as handle:
        for line in handle:
            line = line.split("#", 1)[0].strip()
            if line:
                yield line.split()[-1]


def spec_body(package):
    with open(os.path.join(SPECS, package, package + ".spec"),
              encoding="utf-8") as handle:
        return handle.read().split("%changelog", 1)[0]


class Lib64LayoutTest(unittest.TestCase):
    def test_no_top_level_libraries_in_usr_lib(self):
        offenders = []
        for package, filelist in filelists():
            if package in TOP_LEVEL_ALLOWED:
                continue
            offenders += ["%s: %s" % (package, path) for path in paths(filelist)
                          if TOP_LEVEL_LIB.match(path)]
        self.assertEqual(offenders, [],
                         "architecture libraries belong in /usr/lib64")

    def test_no_pkgconfig_in_usr_lib(self):
        offenders = []
        for package, filelist in filelists():
            if package in PKGCONFIG_ALLOWED:
                continue
            offenders += ["%s: %s" % (package, path) for path in paths(filelist)
                          if path.startswith("/usr/lib/pkgconfig/")]
        self.assertEqual(offenders, [],
                         "pkg-config files belong in /usr/lib64/pkgconfig")

    def test_libdir_defaults_are_overridden(self):
        for package, required in LIBDIR_ARGS.items():
            body = spec_body(package)
            for argument in required:
                self.assertIn(argument, body,
                              "%s does not pass %s" % (package, argument))


if __name__ == "__main__":
    unittest.main()
