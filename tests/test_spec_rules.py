"""Specs follow docs/rules.md "Writing a spec".

Hard rules hold for every spec.  Rules that most specs do not meet yet keep
an allow-list in tests/spec_rules/<rule>.txt (one package directory per
line).  The lists may only shrink: a spec that breaks a rule must be on the
list, and a listed spec that follows the rule must be taken off it.
"""

import os
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPECS = REPO_ROOT / "package_specs"
ALLOW = Path(__file__).resolve().parent / "spec_rules"
sys.path.insert(0, str(REPO_ROOT / "scripts" / "tools"))

import filelist  # noqa: E402  (shared-directory list used by tenko filelist)

OLD_PATCH = re.compile(r"^(%patch\d|%patch \d|%patch -p|\s*patch -N?p\d+ -i )", re.M)
FILES_HEADER = re.compile(r"^%files\b(.*)$")
SECTION = re.compile(
    r"^%(files|changelog|package|description|prep|build|install|check|clean|"
    r"pre|post|preun|postun|pretrans|posttrans|trigger\w*|verifyscript)\b")


def specs():
    for spec in sorted(SPECS.glob("*/*.spec")):
        yield spec.parent.name, spec


def preamble_and_body(spec):
    text = spec.read_text(encoding="utf-8", errors="replace")
    return text.split("\n%changelog", 1)[0]


def inline_file_lists(body):
    """Names of %files sections that list entries inline."""
    lines = body.splitlines()
    found = []
    for i, line in enumerate(lines):
        match = FILES_HEADER.match(line)
        if not match or "-f" in match.group(1).split():
            continue
        j = i + 1
        while j < len(lines) and not SECTION.match(lines[j]):
            if lines[j].strip() and not lines[j].lstrip().startswith("#"):
                found.append(line.strip())
                break
            j += 1
    return found


def owns_shared_dir(spec_dir):
    for path in (spec_dir / "files").glob("*.filelist"):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("%dir ") and line.split(None, 1)[1].strip() in filelist.SKIP_DIRS:
                return True
    return False


def allow_list(rule):
    path = ALLOW / (rule + ".txt")
    names = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.add(line)
    return names


class HardRulesTest(unittest.TestCase):
    def test_every_package_declares_its_sources(self):
        missing = [name for name, spec in specs()
                   if not (spec.parent / "sources").exists()
                   and not (spec.parent / "nosources").exists()]
        self.assertEqual(missing, [], "add a sources file or a nosources marker")

    def test_patches_use_the_patch_macro(self):
        old = [name for name, spec in specs()
               if OLD_PATCH.search(preamble_and_body(spec))]
        self.assertEqual(old, [], "declare PatchN: and apply it with %patch -P N -p1")

    def test_patches_are_applied_in_prep(self):
        # rpm expands %patch only in %prep; elsewhere the shell runs it
        # as a job-control command and the build fails.
        late = []
        for name, spec in specs():
            section = None
            for line in preamble_and_body(spec).splitlines():
                if re.match(r"^%prep\b", line):
                    section = "prep"
                elif re.match(r"^%(build|install|check)(\s|$)", line):
                    section = "other"
                elif line.startswith("%patch") and section == "other":
                    late.append(name)
                    break
        self.assertEqual(late, [], "move %patch into %prep")

    def test_every_spec_has_a_url(self):
        missing = [name for name, spec in specs()
                   if not re.search(r"^URL:", preamble_and_body(spec), re.M)]
        self.assertEqual(missing, [], "add URL: with the upstream project page")

    def test_file_lists_are_static_files(self):
        inline = {name: inline_file_lists(preamble_and_body(spec))
                  for name, spec in specs()}
        inline = {k: v for k, v in inline.items() if v}
        self.assertEqual(inline, {}, "move the entries to files/<package>.filelist "
                         "and use %files -f %{_sourcedir}/<package>.filelist")


class AllowListedRulesTest(unittest.TestCase):
    """Each rule: the set of specs breaking it must equal its allow-list."""

    def check(self, rule, breaks):
        allowed = allow_list(rule)
        existing = {name for name, _ in specs()}
        breaking = {name for name, spec in specs() if breaks(spec)}
        self.assertEqual(sorted(allowed - existing), [],
                         "tests/spec_rules/%s.txt lists unknown packages" % rule)
        self.assertEqual(sorted(breaking - allowed), [],
                         "these specs break the %s rule (docs/rules.md)" % rule)
        self.assertEqual(sorted(allowed - breaking), [],
                         "these specs follow the %s rule now: remove them from "
                         "tests/spec_rules/%s.txt" % (rule, rule))

    def test_filelists_do_not_own_shared_directories(self):
        self.check("shared-dirs", lambda spec: owns_shared_dir(spec.parent))

    def test_build_requires_are_declared(self):
        self.check("buildrequires", lambda spec: (
            not (spec.parent / "nosources").exists()
            and not re.search(r"^BuildRequires:", preamble_and_body(spec), re.M)))


if __name__ == "__main__":
    unittest.main()
