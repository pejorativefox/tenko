import json
import os
import unittest
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(relative):
    with open(os.path.join(REPO_ROOT, relative), encoding="utf-8") as handle:
        return handle.read()


def spec(name):
    return read(os.path.join("package_specs", name, name + ".spec"))


def filelist(name):
    return read(os.path.join("package_specs", name, "files",
                             name + ".filelist"))


def extra_requires():
    text = read("package_specs/tenko-base/requires-extra")
    return [line.split("#", 1)[0].strip()
            for line in text.splitlines()
            if line.split("#", 1)[0].strip()]


class BaseMembershipTest(unittest.TestCase):
    """The console fonts are base packages and reach every install profile."""

    def test_fonts_are_base_membership_and_in_rebuild_order(self):
        base = json.loads(read("package_specs/base.json"))
        for name in ("font-dejavu-sans-mono", "font-noto-cjk",
                     "font-noto-emoji", "font-nerd-symbols"):
            self.assertIn(name, base["packages"])
            self.assertIn(name, base["build_order"])

    def test_runtime_meta_installs_the_console_stack(self):
        # The installer and live media install tenko-base-runtime, not
        # tenko-base; base membership alone does not reach a fresh install.
        runtime = spec("tenko-base-runtime")
        for name in ("kmscon", "libtsm", "font-dejavu-sans-mono",
                     "font-noto-cjk", "font-noto-emoji",
                     "font-nerd-symbols"):
            self.assertIn("Requires:   " + name, runtime)

    def test_base_meta_requires_kmscon(self):
        self.assertIn("kmscon", extra_requires())
        self.assertIn("libtsm", extra_requires())
        self.assertIn("Requires:   kmscon", spec("tenko-base"))
        self.assertIn("Requires:   libtsm", spec("tenko-base"))

    def test_desktop_metas_install_color_emoji(self):
        for name in ("xfce-desktop", "xfce-desktop-core"):
            self.assertIn("Requires:   font-noto-color-emoji", spec(name))


class FontConfigTest(unittest.TestCase):
    """Each font package appends its face without replacing the primary one."""

    def test_font_packages_ship_a_fontconfig_snippet(self):
        expected = {
            "font-dejavu-sans-mono": "DejaVu Sans Mono",
            "font-noto-cjk": "Noto Sans Mono CJK SC",
            "font-noto-emoji": "Noto Emoji",
            "font-nerd-symbols": "Symbols Nerd Font Mono",
            "font-noto-color-emoji": "Noto Color Emoji",
        }
        for package, family in expected.items():
            path = os.path.join("package_specs", package, "files",
                                "69-tenko-" + package.split("font-", 1)[1]
                                + ".conf")
            self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, path)),
                            path)
            self.assertIn(family, read(path))
            # Every snippet must append the family weakly; a plain prefer
            # would replace the user's terminal font.
            self.assertIn('mode="append" binding="weak"', read(path))

    def test_dejavu_fallback_precedes_cjk_and_emoji(self):
        # DejaVu supplies Dingbats/Misc Symbols and keeps a single-cell
        # metric for characters Noto CJK also covers (for example U+25D1).
        # It must be appended before the CJK and emoji snippets, whose
        # filenames sort after it.
        snippet = "69-tenko-dejavu-sans-mono.conf"
        for later in ("69-tenko-nerd-symbols.conf", "69-tenko-noto-cjk.conf",
                      "69-tenko-noto-color-emoji.conf",
                      "69-tenko-noto-emoji.conf"):
            self.assertLess(snippet, later)

    def test_dejavu_fallback_covers_concrete_monospace_families(self):
        # A terminal that requests "Terminus (TTF)" never matches the
        # generic "monospace" family, so the snippet also appends the face
        # to any pattern that declares monospaced spacing.
        text = read("package_specs/font-dejavu-sans-mono/files/"
                    "69-tenko-dejavu-sans-mono.conf")
        self.assertIn('<test name="spacing" compare="eq">'
                      '<const>mono</const></test>', text)

    def test_console_family_prefers_the_monochrome_emoji_face(self):
        text = read("package_specs/kmscon/files/69-tenko-console.conf")
        root = ET.fromstring(text)
        values = [value.text for value in root.iter("string")]
        self.assertIn("DejaVu Sans Mono", values)
        self.assertLess(values.index("DejaVu Sans Mono"),
                        values.index("Noto Emoji"))
        self.assertLess(values.index("Noto Emoji"),
                        values.index("Symbols Nerd Font Mono"))
        self.assertNotIn("Noto Color Emoji", values)

    def test_kmscon_config_uses_the_alias(self):
        self.assertIn("font-name=Tenko Console",
                      read("package_specs/kmscon/files/kmscon.conf"))


class ActivationTest(unittest.TestCase):
    """kmscon replaces getty on tty1 without fighting the GUI or installer."""

    def test_preset_disables_getty_and_enables_the_vt_instance(self):
        preset = read("package_specs/kmscon/files/50-tenko-console.preset")
        self.assertIn("disable getty@.service", preset)
        self.assertIn("disable kmscon.service", preset)
        self.assertIn("enable kmsconvt@.service", preset)
        # Preset files are first-match; it must sort before systemd's.
        self.assertLess("50-tenko-console.preset", "90-systemd.preset")

    def test_lightdm_releases_tty1_before_taking_drm(self):
        service = read("package_specs/lightdm/files/lightdm.service")
        self.assertIn("Conflicts=getty@tty1.service kmsconvt@tty1.service",
                      service)
        self.assertIn("After=getty@tty1.service kmsconvt@tty1.service",
                      service)

    def test_live_installer_keeps_tty1(self):
        service = read(
            "package_specs/tenko-installer/files/tenko-installer.service")
        self.assertIn("Before=getty@tty1.service kmsconvt@tty1.service",
                      service)
        # A conflict would stop kmscon even when the live condition is false.
        self.assertNotIn("Conflicts=getty@tty1.service kmsconvt@tty1.service",
                         service)

    def test_firstboot_prompt_keeps_tty1(self):
        service = read(
            "package_specs/tenko-firstboot/files/"
            "tenko-firstboot-root-password.service")
        self.assertIn("Before=getty@tty1.service kmsconvt@tty1.service",
                      service)
        # Conflicts= would enqueue a stop job even when the first-boot
        # condition is false, deleting kmscon's start job on a normal boot.
        self.assertNotIn("Conflicts=kmsconvt@tty1.service", service)

    def test_kmscon_unit_drops_the_tty0_condition(self):
        # The condition races devtmpfs on an initramfs-less boot.
        self.assertIn(
            "sed -i '/^ConditionPathExists=\\/dev\\/tty0$/d'", spec("kmscon"))

    def test_kmscon_package_files_are_complete(self):
        files = filelist("kmscon")
        for path in ("/usr/bin/kmscon",
                     "/usr/lib64/kmscon/mod-freetype.so",
                     "/usr/lib64/kmscon/mod-psf.so",
                     "/usr/lib64/kmscon/mod-unifont.so",
                     "/usr/lib/systemd/system/kmsconvt@.service",
                     "/usr/lib/systemd/system-preset/50-tenko-console.preset",
                     "/etc/fonts/conf.d/69-tenko-console.conf"):
            self.assertIn(path, files)


if __name__ == "__main__":
    unittest.main()
