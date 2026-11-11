"""Helpers for tests that inspect package specs.

Specs list their payload in static filelists (`%files -f
%{_sourcedir}/<name>.filelist`, the file in package_specs/<pkg>/files/).
`with_filelists()` returns the spec text with each such list inlined after
its `%files` line, so a test can look for a payload path no matter where
the spec keeps it.
"""

import os
import re

FILES_F = re.compile(r"^(%files\b.*?)\s+-f\s+%\{_sourcedir\}/(\S+)(.*)$")


def with_filelists(text, spec_dir):
    out = []
    for line in text.splitlines():
        match = FILES_F.match(line)
        if not match:
            out.append(line)
            continue
        out.append((match.group(1) + match.group(3)).rstrip())
        path = os.path.join(spec_dir, "files", match.group(2))
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as handle:
                out.extend(handle.read().splitlines())
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def read_spec(path):
    """Read a spec file with its filelists inlined."""
    with open(path, encoding="utf-8") as handle:
        return with_filelists(handle.read(), os.path.dirname(path))


def expand_if_spec(text, path):
    """Inline the filelists when PATH is a spec; return TEXT otherwise."""
    path = str(path)
    if path.endswith(".spec"):
        return with_filelists(text, os.path.dirname(path))
    return text
