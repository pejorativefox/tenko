import os
import re
import unittest
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(REPO_ROOT, "package_specs", "tenko-desktop-config",
                    "tenko-desktop-config.spec")


def spec_text():
    with open(SPEC, encoding="utf-8") as handle:
        return handle.read()


def xfconf_default(text, name):
    """Return the XML body of an /etc/skel xfconf channel heredoc."""
    pattern = re.compile(
        r"cat > \"\$xfconfdir/%s\" <<'EOF'\n(.*?)\nEOF" % re.escape(name),
        re.S)
    match = pattern.search(text)
    if match is None:
        raise AssertionError("spec does not write %s" % name)
    return ET.fromstring(match.group(1))


class DesktopDefaultsTest(unittest.TestCase):
    """New accounts get Tenko's look and layout from /etc/skel."""

    def test_panel_default_is_installed_for_new_users(self):
        self.assertIn(
            "%config(noreplace) "
            "%{_sysconfdir}/skel/.config/xfce4/xfconf/xfce-perchannel-xml/"
            "xfce4-panel.xml",
            spec_text())

    def test_panel_default_has_only_the_top_panel(self):
        # xfce4-panel otherwise seeds the account from
        # /etc/xdg/xfce4/panel/default.xml, whose panel-2 sits at the bottom.
        root = xfconf_default(spec_text(), "xfce4-panel.xml")
        panels = root.find("./property[@name='panels']")
        self.assertIsNotNone(panels)
        ids = [value.get("value") for value in panels.findall("value")]
        self.assertEqual(ids, ["1"])
        self.assertIsNone(panels.find("property[@name='panel-2']"))

        panel = panels.find("property[@name='panel-1']")
        self.assertEqual(
            panel.find("property[@name='position']").get("value"),
            "p=6;x=0;y=0")
        self.assertEqual(
            [value.get("value")
             for value in panel.find("property[@name='plugin-ids']")],
            [str(i) for i in range(1, 11)])

    def test_panel_plugins_are_defined(self):
        root = xfconf_default(spec_text(), "xfce4-panel.xml")
        plugins = root.find("./property[@name='plugins']")
        for i in range(1, 11):
            self.assertIsNotNone(
                plugins.find("property[@name='plugin-%d']" % i))

    def test_theme_defaults_are_installed_for_new_users(self):
        text = spec_text()
        xsettings = xfconf_default(text, "xsettings.xml")
        xfwm4 = xfconf_default(text, "xfwm4.xml")
        self.assertEqual(
            xsettings.find(
                "./property[@name='Net']/property[@name='ThemeName']"
            ).get("value"),
            "Arc-Dark")
        self.assertEqual(
            xfwm4.find("./property[@name='general']/property[@name='theme']"
                       ).get("value"),
            "Arc-Dark")


if __name__ == "__main__":
    unittest.main()
