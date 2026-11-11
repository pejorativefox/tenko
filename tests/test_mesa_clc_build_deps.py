import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")

CLC_BUILD_PACKAGES = {
    "llvm-devel",
    "llvm",
    "llvm-static",
    "clang-libs",
    "clang-devel",
    "clang-resource-filesystem",
    "spirv-headers",
    "spirv-tools",
    "spirv-llvm-translator",
    "python-mako",
    "python-pyyaml",
}

# Packages that are built from their own spec (clang-libs and
# clang-resource-filesystem are subpackages of llvm).
SPEC_PACKAGES = {
    "spirv-headers",
    "spirv-tools",
    "spirv-llvm-translator",
    "python-mako",
    "python-pyyaml",
}

# Mesa links the installed SPIRV libraries and reads clang's resource files;
# it does not use the SPIRV headers directly.  It does need the llvm tools
# and static archives: find_package(LLVM) loads LLVMExports.cmake, which
# checks every installed tool binary and archive.
MESA_BUILD_PACKAGES = CLC_BUILD_PACKAGES - {"spirv-headers"}


def spec_path(relative):
    return os.path.join(SPECS, relative)


def read(relative):
    with open(spec_path(relative), encoding="utf-8") as handle:
        return handle.read()


def spec_body(relative):
    return read(relative).split("%changelog", 1)[0]


def requires(text):
    """Expand Requires:/BuildRequires: lines into a set of package names.

    Both comma-separated single-line lists and one-name-per-line forms are
    accepted.  Version constraints are discarded.
    """
    names = set()
    for line in text.splitlines():
        match = re.match(r"^(?:Build)?Requires:\s+(.*)$", line)
        if not match:
            continue
        for item in match.group(1).split(","):
            name = item.strip().split()[0] if item.strip() else ""
            if name and not name.startswith("%"):
                names.add(name)
    return names


class MesaClcBuildDepsTest(unittest.TestCase):
    """Mesa's iris/crocus drivers build mesa_clc, which needs LLVMSPIRVLib,
    SPIRV-Tools, Clang's opencl-c.h and the Mako/PyYAML Python modules.  Those
    are build-only inputs, but a clean Mesa rebuild must be reproducible
    without the local placeholder-image workaround (issue #51)."""

    def test_package_specs_exist(self):
        for package in SPEC_PACKAGES:
            spec = "%s/%s.spec" % (package, package)
            self.assertTrue(os.path.isfile(spec_path(spec)),
                            "%s is missing" % spec)
            self.assertTrue(
                read("%s/sources" % package).strip(),
                "%s/sources must record provenance" % package)

    def test_build_environment_does_not_carry_the_chain(self):
        """The chain is Mesa's build input, declared in mesa.spec; the
        development meta must not hide a missing BuildRequires (#58)."""
        required = requires(spec_body("tenko-base-build/tenko-base-build.spec"))
        self.assertEqual(CLC_BUILD_PACKAGES & required, set())

    def test_mesa_declares_the_build_chain(self):
        required = requires(spec_body("mesa/mesa.spec"))
        missing = MESA_BUILD_PACKAGES - required
        self.assertEqual(
            missing, set(),
            "mesa.spec must BuildRequire the CLC build chain: %s"
            % ", ".join(sorted(missing)))

    def test_mesa_builds_against_real_llvm_files(self):
        required = requires(spec_body("mesa/mesa.spec"))
        self.assertIn(
            "llvm-static", required,
            "LLVMExports.cmake verifies the static archives, and the published "
            "llvm-devel does not require llvm-static")
        self.assertIn(
            "llvm", required,
            "LLVMExports.cmake verifies the tool binaries, and the published "
            "llvm-devel does not require the llvm tools package")

    def test_translator_uses_the_real_llvm_packages(self):
        body = spec_body("spirv-llvm-translator/spirv-llvm-translator.spec")
        required = requires(body)
        for package in ("llvm-devel", "llvm-static", "llvm", "spirv-headers"):
            self.assertIn(package, required,
                          "translator must build against %s" % package)
        self.assertNotRegex(
            body, r"(?i)placeholder|stub llvm-tblgen|zero-length",
            "the translator must not depend on the old placeholder workaround")

    def test_spirv_headers_pin_the_translator_requirement(self):
        spec = read("spirv-headers/spirv-headers.spec")
        sources = read("spirv-headers/sources")
        self.assertIn("cb42dec3830d3ac67fa449ecdc0c0f73d5e74498", spec)
        self.assertIn("cb42dec3830d3ac67fa449ecdc0c0f73d5e74498", sources,
                      "SPIRV-Headers must follow the translator's pinned commit")

    def test_translator_ships_its_shared_library(self):
        entries = {
            line.strip()
            for line in read(
                "spirv-llvm-translator/files/"
                "spirv-llvm-translator.filelist").splitlines()
        }
        self.assertIn("/usr/lib64/libLLVMSPIRVLib.so.23.1", entries)
        self.assertIn("/usr/lib64/pkgconfig/LLVMSPIRVLib.pc", entries)
        self.assertNotIn("/usr/lib64/libLLVMSPIRVLib.a", entries,
                         "Mesa links LLVMSPIRVLib through its pkg-config file")

    def test_spirv_tools_ships_static_libraries_and_tools(self):
        entries = {
            line.strip()
            for line in read(
                "spirv-tools/files/spirv-tools.filelist").splitlines()
        }
        self.assertIn("/usr/lib64/libSPIRV-Tools.a", entries)
        self.assertIn("/usr/lib64/libSPIRV-Tools-opt.a", entries)
        self.assertIn("/usr/lib64/libSPIRV-Tools-shared.so", entries)
        self.assertIn("/usr/lib64/pkgconfig/SPIRV-Tools.pc", entries)
        self.assertIn("/usr/bin/spirv-opt", entries)


if __name__ == "__main__":
    unittest.main()
