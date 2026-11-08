import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")


def read(relative):
    with open(os.path.join(REPO_ROOT, relative), encoding="utf-8") as handle:
        return handle.read()


def spec_lines(relative):
    with open(os.path.join(SPECS, relative), encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    changelog = next((i for i, line in enumerate(lines)
                      if line.startswith("%changelog")), len(lines))
    return lines[:changelog]


def has_require(lines, name):
    pattern = re.compile(r"^Requires:\s+%s\s*$" % re.escape(name))
    return any(pattern.match(line) for line in lines)


class FlatpakSupportTest(unittest.TestCase):
    """A desktop install can use flatpak without sudo or a restart: the
    default admin is in wheel, wheel may configure system remotes, Flathub
    exists, an authentication agent is autostarted and portals work."""

    def test_wheel_may_configure_remotes_and_install_bundles(self):
        rule = read("package_specs/flatpak/files/50-tenko-flatpak.rules")
        self.assertIn("org.freedesktop.Flatpak.configure-remote", rule)
        self.assertIn("org.freedesktop.Flatpak.install-bundle", rule)
        self.assertIn('subject.isInGroup("wheel")', rule)
        self.assertIn("polkit.Result.YES", rule)

    def test_flatpak_ships_the_rule_as_system_config(self):
        spec = read("package_specs/flatpak/flatpak.spec")
        self.assertIn(
            "install -Dpm0644 %{_sourcedir}/50-tenko-flatpak.rules", spec)
        self.assertIn("50-tenko-flatpak.rules", read(
            "package_specs/flatpak/files/flatpak.filelist"))
        self.assertIn(
            "%config(noreplace) "
            "/etc/polkit-1/rules.d/50-tenko-flatpak.rules",
            read("package_specs/flatpak/files/flatpak.filelist"))

    def test_flatpak_ships_the_flathub_remote(self):
        remote = read("package_specs/flatpak/files/flathub.flatpakrepo")
        self.assertIn("[Flatpak Repo]", remote)
        self.assertIn("Url=https://dl.flathub.org/repo/", remote)
        self.assertIn("GPGKey=", remote)
        spec = read("package_specs/flatpak/flatpak.spec")
        self.assertIn("%{_sourcedir}/flathub.flatpakrepo", spec)
        self.assertIn(
            "/usr/share/flatpak/remotes.d/flathub.flatpakrepo",
            read("package_specs/flatpak/files/flatpak.filelist"))

    def test_desktop_profiles_require_flatpak_support(self):
        packages = ("flatpak", "xfce-polkit", "xdg-desktop-portal",
                    "xdg-desktop-portal-gtk")
        for spec in ("xfce-desktop/xfce-desktop.spec",
                     "xfce-desktop-core/xfce-desktop-core.spec"):
            lines = spec_lines(spec)
            for package in packages:
                self.assertTrue(
                    has_require(lines, package),
                    "%s must require %s" % (spec, package))

    def test_polkit_agent_is_autostarted(self):
        lines = spec_lines("xfce-polkit/xfce-polkit.spec")
        self.assertIn("/etc/xdg/autostart/xfce-polkit.desktop", lines)
        self.assertIn("/usr/libexec/xfce-polkit", lines)
        self.assertIn("Requires:   polkit", lines)

    def test_portal_backend_ships_its_descriptor(self):
        lines = spec_lines("xdg-desktop-portal-gtk/xdg-desktop-portal-gtk.spec")
        self.assertTrue(has_require(lines, "xdg-desktop-portal"))
        filelist = read(
            "package_specs/xdg-desktop-portal-gtk/files/"
            "xdg-desktop-portal-gtk.filelist")
        self.assertIn("/usr/share/xdg-desktop-portal/portals/gtk.portal",
                      filelist)

    def test_default_admin_is_in_wheel(self):
        # The wheel rule above only helps if the installer puts the default
        # user in wheel; the desktop has no other admin path.
        install = read("package_specs/tenko-installer/files/install.py")
        self.assertIn('groups = ("wheel", "kvm")', install)


if __name__ == "__main__":
    unittest.main()
