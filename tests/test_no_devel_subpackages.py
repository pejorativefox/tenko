import glob
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")

# LLVM/Clang keep the Fedora-style toolchain split: their -devel packages are
# intentional and support parallel compiler installations.
ALLOWED_DEVEL = {"llvm-devel", "clang-devel"}


def spec_files():
    return sorted(glob.glob(os.path.join(SPECS, "*", "*.spec")))


def body_before_changelog(path):
    with open(path, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    changelog = next((i for i, line in enumerate(lines)
                      if line.startswith("%changelog")), len(lines))
    return lines[:changelog]


def spec_name(lines):
    for line in lines:
        match = re.match(r"^Name:\s*(\S+)", line)
        if match:
            return match.group(1)
    return ""


def section_package(line, name):
    """Return the binary package a %package/%description/%files line targets."""
    parts = line.split()
    if len(parts) >= 3 and parts[1] == "-n":
        return parts[2]
    if len(parts) >= 2 and parts[1] not in ("-n", "-f"):
        suffix = parts[1]
        return "%s-%s" % (name, suffix)
    return "%s" % name


class NoDevelSubpackagesTest(unittest.TestCase):
    """Only llvm-devel and clang-devel may remain as -devel subpackages;
    every other package ships its development payload in the runtime RPM."""

    def test_no_unexpected_devel_sections(self):
        pattern = re.compile(
            r"^%(package|description|files)\s+(-n\s+\S+|\S+)")
        offenders = []
        for spec in spec_files():
            lines = body_before_changelog(spec)
            name = spec_name(lines)
            for line in lines:
                if not pattern.match(line):
                    continue
                if line.startswith("%files") and "-f" not in line:
                    continue
                package = section_package(line, name)
                if package.endswith("-devel") and package not in ALLOWED_DEVEL:
                    offenders.append("%s: %s" % (spec, line))
        self.assertEqual(offenders, [])

    def test_no_unexpected_devel_filelists(self):
        found = []
        for path in glob.glob(os.path.join(SPECS, "*", "files",
                                           "*-devel.filelist")):
            package = os.path.basename(path)[:-len(".filelist")]
            if package not in ALLOWED_DEVEL:
                found.append(path)
        self.assertEqual(found, [])

    def test_no_unexpected_devel_requirements(self):
        token = re.compile(r"\b([A-Za-z0-9+_.-]+-devel)\b")
        offenders = []
        for spec in spec_files():
            for line in body_before_changelog(spec):
                if not re.match(
                        r"^(Requires|BuildRequires|Recommends|Suggests|"
                        r"Provides|Obsoletes|Conflicts):", line):
                    continue
                for package in token.findall(line):
                    if package not in ALLOWED_DEVEL:
                        offenders.append("%s: %s" % (spec, line))
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
