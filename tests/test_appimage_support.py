import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")

FUSE2_SPEC = "fuse2/fuse2.spec"
FUSE2_FILELIST = "fuse2/files/fuse2.filelist"

SECTION = re.compile(
    r"^%(description|prep|build|install|check|clean|files|changelog|"
    r"post|postun|pre|preun|package)\b")


def spec_path(relative):
    return os.path.join(SPECS, relative)


def read(relative):
    with open(spec_path(relative), encoding="utf-8") as handle:
        return handle.read()


def spec_lines(relative):
    with open(spec_path(relative), encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    changelog = next((i for i, line in enumerate(lines)
                      if line.startswith("%changelog")), len(lines))
    return lines[:changelog]


def has_require(lines, name):
    pattern = re.compile(r"^Requires:\s+%s\s*$" % re.escape(name))
    return any(pattern.match(line) for line in lines)


def files_section(text):
    """Return only the %files body so comments elsewhere cannot satisfy or
    break the packaging checks below."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines)
                  if re.match(r"^%files\b", line)), None)
    if start is None:
        return ""
    body = []
    for line in lines[start + 1:]:
        if SECTION.match(line):
            break
        body.append(line)
    return "\n".join(body)


class AppImageSupportTest(unittest.TestCase):
    """AppImage type-2 executables need libfuse.so.2: the runtime dlopens it
    and fuse3 ships a different soname.  A desktop install must ship the FUSE
    2 runtime without pulling in a -devel subpackage or fuse3's config."""

    def test_fuse2_package_identity(self):
        path = spec_path(FUSE2_SPEC)
        self.assertTrue(os.path.isfile(path), "%s is missing" % FUSE2_SPEC)
        spec = read(FUSE2_SPEC)
        self.assertRegex(spec, r"(?m)^Name:\s+fuse2\s*$")
        self.assertRegex(spec, r"(?m)^Version:\s+2\.9\.9\s*$")

    def test_fuse2_provides_libfuse2(self):
        spec = read(FUSE2_SPEC)
        self.assertRegex(
            spec, r"(?m)^Provides:\s+libfuse2(?:\s|$)",
            "fuse2 must Provide: libfuse2 so packages can depend on the "
            "runtime by capability")

    def test_fuse2_ships_the_fuse2_soname(self):
        path = os.path.join(SPECS, FUSE2_FILELIST)
        self.assertTrue(os.path.isfile(path), "%s is missing" % FUSE2_FILELIST)
        entries = {line.strip() for line in read(FUSE2_FILELIST).splitlines()}
        for wanted in ("/usr/lib64/libfuse.so.2",
                       "/usr/lib64/libfuse.so.2.9.9",
                       "/usr/bin/fusermount"):
            self.assertIn(wanted, entries,
                          "%s must ship %s" % (FUSE2_FILELIST, wanted))

    def test_desktop_profiles_require_fuse2(self):
        for spec in ("xfce-desktop/xfce-desktop.spec",
                     "xfce-desktop-core/xfce-desktop-core.spec"):
            lines = spec_lines(spec)
            self.assertTrue(
                has_require(lines, "fuse2"),
                "%s must require fuse2 for AppImage type-2 support" % spec)

    def test_fuse2_has_no_devel_subpackage(self):
        spec = read(FUSE2_SPEC)
        self.assertIsNone(
            re.search(r"(?m)^%package\s+devel\b", spec),
            "fuse2 must not ship a -devel subpackage; Tenko keeps headers, "
            ".pc files and unversioned links in the runtime package")

    def test_fuse2_leaves_fuse3_owned_paths_alone(self):
        spec = read(FUSE2_SPEC)
        filelist = read(FUSE2_FILELIST)
        for owned in ("/etc/fuse.conf", "/dev/fuse"):
            self.assertNotIn(
                owned, filelist,
                "%s must not package %s; fuse3 owns it" % (FUSE2_FILELIST,
                                                           owned))
            self.assertNotIn(
                owned, files_section(spec),
                "%s must not package %s; fuse3 owns it" % (FUSE2_SPEC, owned))


if __name__ == "__main__":
    unittest.main()
