import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")


def read(relative):
    with open(os.path.join(SPECS, relative), encoding="utf-8") as handle:
        return handle.read()


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
        "go/go-bin.spec",
        "nodejs/nodejs.spec",
        "rust/rust.spec",
        "dotnet-bin/dotnet-bin.spec",
        "podman-bin/podman-bin.spec",
        "kitty-bin/kitty-bin.spec",
        "firefox-bin/firefox-bin.spec",
        "google-chrome-bin/google-chrome-bin.spec",
    )

    def test_bundles_link_commands_into_usr_bin(self):
        for spec in self.BUNDLES:
            body = before_changelog(read(spec))
            self.assertIn("ln -s", body, spec)
            self.assertTrue("%{_bindir}" in body or "/usr/bin" in body,
                            "%s has no /usr/bin entry point" % spec)

    def test_go_commands_are_linked_into_usr_bin(self):
        body = before_changelog(read("go/go-bin.spec"))
        self.assertIn("ln -s /opt/go/bin/go %{buildroot}%{_bindir}/go", body)
        self.assertIn("ln -s /opt/go/bin/gofmt %{buildroot}%{_bindir}/gofmt",
                      body)
        self.assertIn("%{_bindir}/go", body.split("%files", 1)[1])

    def test_go_profile_snippet_is_not_the_only_entry_point(self):
        script = heredoc(read("go/go-bin.spec"), "/etc/profile.d/go_path.sh")
        self.assertIn("export GOROOT=/opt/go", script)
        # profile.d is a convenience for login shells; the PATH update must
        # not duplicate entries when the snippet is read twice.
        self.assertIn('case ":$PATH:" in', script)


if __name__ == "__main__":
    unittest.main()
