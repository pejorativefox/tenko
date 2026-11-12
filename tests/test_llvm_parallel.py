"""The LLVM 22 packages are a parallel toolchain, not a replacement for 23.

llvm22 installs a complete tree under /usr/lib64/llvm22 and only adds
command links with a -22 suffix, so `dnf install llvm22` next to the
distribution llvm/clang 23 packages cannot overwrite files from either.
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE = os.path.join(REPO_ROOT, "package_specs", "llvm22")
SPEC = os.path.join(PACKAGE, "llvm22.spec")
FILELIST = os.path.join(PACKAGE, "files", "llvm22.filelist")

PAYLOAD_ROOTS = ("/usr/lib64/llvm22", "/etc/clang-22")
COMMAND_ROOT = "/usr/bin/"


def spec_body():
    with open(SPEC, encoding="utf-8") as handle:
        return handle.read().split("%changelog", 1)[0]


def filelist_paths():
    with open(FILELIST, encoding="utf-8") as handle:
        for line in handle:
            line = line.split("#", 1)[0].strip()
            if line:
                yield line.split()[-1]


class LlvmParallelInstallTest(unittest.TestCase):
    def test_major_version_is_22(self):
        self.assertRegex(spec_body(), r"(?m)^Version:\s+22\.")

    def test_install_prefix_is_versioned(self):
        body = spec_body()
        self.assertIn("CMAKE_INSTALL_PREFIX=%{_libdir}/llvm22", body)
        self.assertIn("CLANG_CONFIG_FILE_SYSTEM_DIR=%{_sysconfdir}/clang-22",
                      body)

    def test_commands_are_suffixed(self):
        for path in filelist_paths():
            if path.startswith(COMMAND_ROOT):
                self.assertTrue(
                    path.endswith("-22"),
                    "unversioned command link would collide with llvm 23: "
                    + path)

    def test_payload_is_versioned(self):
        for path in filelist_paths():
            if path.startswith(COMMAND_ROOT):
                continue
            self.assertTrue(
                any(path == root or path.startswith(root + "/")
                    for root in PAYLOAD_ROOTS),
                "path outside the parallel install tree: " + path)


if __name__ == "__main__":
    unittest.main()
