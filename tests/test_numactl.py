"""libnuma tools coexist with the kernel syscall documentation in man-pages."""

import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "package_specs" / "numactl"


class NumactlPackagingTest(unittest.TestCase):
    def test_kernel_syscall_manual_is_removed_during_install(self):
        spec = (PACKAGE / "numactl.spec").read_text(encoding="utf-8")
        install = spec.split("\n%install\n", 1)[1].split("\n%files", 1)[0]
        self.assertIn("rm -f %{buildroot}%{_mandir}/man2/move_pages.2", install)
        self.assertIn("%{buildroot}%{_mandir}/man2/move_pages.2.gz", install)

    def test_only_libnuma_and_tool_manuals_are_packaged(self):
        lines = (PACKAGE / "files" / "numactl.filelist").read_text(
            encoding="utf-8").splitlines()
        paths = {line.split()[-1] for line in lines if line.strip()}
        self.assertFalse(any("/man2/" in path for path in paths))
        for path in ("/usr/lib64/libnuma.so.1", "/usr/bin/numactl",
                     "/usr/share/man/man3/numa.3.gz",
                     "/usr/share/man/man8/numactl.8.gz"):
            with self.subTest(path=path):
                self.assertIn(path, paths)


if __name__ == "__main__":
    unittest.main()
