import os
import re
import unittest

from specutil import expand_if_spec as _expand_spec

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")


def read(relative):
    with open(os.path.join(SPECS, relative), encoding="utf-8") as handle:
        return _expand_spec(handle.read(), os.path.join(SPECS, relative))


def before_changelog(text):
    return text.split("%changelog", 1)[0]


def heredoc(text, path, marker="EOF"):
    pattern = re.compile(
        r"cat > %%\{buildroot\}%s << \"?%s\"?\n(.*?)\n%s"
        % (re.escape(path), re.escape(marker), re.escape(marker)), re.S)
    match = pattern.search(text)
    if match is None:
        raise AssertionError("spec does not write " + path)
    return match.group(1)


class OptBundleTest(unittest.TestCase):
    """Third-party /opt bundles expose commands through /usr/bin."""

    BUNDLES = (
        "nodejs/nodejs.spec",
        "dotnet-bin/dotnet-bin.spec",
        "podman-bin/podman-bin.spec",
        "firefox-bin/firefox-bin.spec",
        "google-chrome-bin/google-chrome-bin.spec",
    )

    def test_bundles_link_commands_into_usr_bin(self):
        for spec in self.BUNDLES:
            body = before_changelog(read(spec))
            self.assertIn("ln -s", body, spec)
            self.assertTrue("%{_bindir}" in body or "/usr/bin" in body,
                            "%s has no /usr/bin entry point" % spec)

    def test_rust_is_a_distro_toolchain_not_an_opt_bundle(self):
        """rust is built from source, so it installs under /usr, not /opt."""
        body = before_changelog(read("rust/rust.spec"))
        self.assertNotIn("/opt", body)
        self.assertIn('prefix = "%{_prefix}"', body)
        self.assertIn('libdir = "lib64"', body)

    def test_go_is_a_distro_toolchain_not_an_opt_bundle(self):
        """go is built from source, so it lives in /usr/lib64/go, not /opt."""
        body = before_changelog(read("go/go.spec"))
        self.assertNotIn("/opt", body)
        self.assertNotIn("profile.d", body)
        self.assertIn("ln -s ../lib64/go/bin/go %{buildroot}%{_bindir}/go", body)
        self.assertIn("ln -s ../lib64/go/bin/gofmt %{buildroot}%{_bindir}/gofmt",
                      body)


if __name__ == "__main__":
    unittest.main()
