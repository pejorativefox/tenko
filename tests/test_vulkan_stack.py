import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")

# The Vulkan ICDs that match the distro's GPUs and its software fallback:
# RADV (AMD GCN1+), ANV (Intel Gen8+), Hasvk (Intel Gen4-7.5) and lavapipe.
EXPECTED_VULKAN_DRIVERS = {"amd", "intel", "intel_hasvk", "swrast"}
EXPECTED_ICD_LIBRARIES = {
    "libvulkan_radeon.so",
    "libvulkan_intel.so",
    "libvulkan_intel_hasvk.so",
    "libvulkan_lvp.so",
}
EXPECTED_ICD_MANIFESTS = {
    "radeon_icd.x86_64.json",
    "intel_icd.x86_64.json",
    "intel_hasvk_icd.x86_64.json",
    "lvp_icd.x86_64.json",
}


def spec_path(relative):
    return os.path.join(SPECS, relative)


def read(relative):
    with open(spec_path(relative), encoding="utf-8") as handle:
        return handle.read()


def spec_body(relative):
    return read(relative).split("%changelog", 1)[0]


def requires(text):
    """Expand Requires:/BuildRequires: lines into a set of package names."""
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


def filelist(relative):
    entries = {
        os.path.basename(line.strip())
        for line in read(relative).splitlines()
        if line.strip()
    }
    return entries


class VulkanStackTest(unittest.TestCase):
    """A Vulkan consumer needs the Khronos loader, an installed ICD from
    Mesa and the headers that the loader builds from.  A missing piece makes
    SDL_CreateGPUDevice fail with no backend, so the three packages must stay
    wired together."""

    def test_packages_record_their_upstream_release(self):
        for package in ("vulkan-headers", "vulkan-loader"):
            spec = "%s/%s.spec" % (package, package)
            self.assertTrue(os.path.isfile(spec_path(spec)), "%s is missing" % spec)
            sources = read("%s/sources" % package)
            self.assertIn("vulkan-sdk-1.4.363.0", sources,
                          "%s must record the Vulkan SDK release" % package)

    def test_loader_builds_against_the_headers(self):
        required = requires(spec_body("vulkan-loader/vulkan-loader.spec"))
        self.assertIn("vulkan-headers", required)

    def test_build_environment_does_not_hide_the_headers(self):
        """vulkan-loader declares vulkan-headers itself; the development
        meta must not mask a missing BuildRequires (issue #58)."""
        required = requires(spec_body("tenko-base-build/tenko-base-build.spec"))
        self.assertNotIn("vulkan-headers", required)

    def test_mesa_builds_the_vulkan_drivers(self):
        match = re.search(r"-Dvulkan-drivers=([^\s\\]+)",
                          spec_body("mesa/mesa.spec"))
        self.assertIsNotNone(match, "mesa.spec has no -Dvulkan-drivers")
        drivers = set(match.group(1).split(","))
        self.assertEqual(EXPECTED_VULKAN_DRIVERS - drivers, set())

    def test_mesa_requires_the_loader(self):
        required = requires(spec_body("mesa/mesa.spec"))
        self.assertIn("vulkan-loader", required)

    def test_mesa_filelist_ships_the_icds(self):
        entries = filelist("mesa/files/mesa.filelist")
        self.assertEqual(EXPECTED_ICD_LIBRARIES - entries, set())
        self.assertEqual(EXPECTED_ICD_MANIFESTS - entries, set())

    def test_loader_filelist_is_complete(self):
        entries = filelist("vulkan-loader/files/vulkan-loader.filelist")
        self.assertIn("libvulkan.so.1.4.363", entries)
        self.assertIn("vulkan.pc", entries,
                      "the no -devel rule keeps vulkan.pc in the runtime package")
        self.assertIn("icd.d", entries,
                      "the loader owns the ICD directory")


if __name__ == "__main__":
    unittest.main()
