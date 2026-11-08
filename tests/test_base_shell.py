import json
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(REPO_ROOT, "package_specs")


def read(relative):
    with open(os.path.join(REPO_ROOT, relative), encoding="utf-8") as handle:
        return handle.read()


def heredoc(text, path, marker="EOF2"):
    pattern = re.compile(
        r"cat > %%\{buildroot\}%s <<'%s'\n(.*?)\n%s"
        % (re.escape(path), re.escape(marker), re.escape(marker)), re.S)
    match = pattern.search(text)
    if match is None:
        raise AssertionError("spec does not write " + path)
    return match.group(1)


class BaseShellTest(unittest.TestCase):
    """bash-completion is base membership and reaches a new user's terminal."""

    def test_completion_is_part_of_the_base_set(self):
        base = json.loads(read("package_specs/base.json"))
        self.assertIn("bash-completion", base["packages"])
        self.assertIn("bash-completion", base["build_order"])
        self.assertGreater(base["build_order"].index("bash-completion"),
                           base["build_order"].index("bash"))

    def test_completion_is_not_an_extra_any_more(self):
        extra = read("package_specs/tenko-base/requires-extra")
        names = [line.split("#", 1)[0].strip() for line in extra.splitlines()]
        self.assertNotIn("bash-completion", names)
        self.assertIn("Requires:   bash-completion",
                      read("package_specs/tenko-base/tenko-base.spec"))

    def test_new_users_get_login_and_interactive_startup_files(self):
        spec = read("package_specs/tenko-sysconfig/tenko-sysconfig.spec")
        self.assertIn("%dir /etc/skel", spec)
        self.assertIn("%config(noreplace) /etc/skel/.bash_profile", spec)
        self.assertIn("%config(noreplace) /etc/skel/.bashrc", spec)

        profile = heredoc(spec, "/etc/skel/.bash_profile")
        self.assertIn('. "$HOME/.bashrc"', profile)
        # Bash reads /etc/profile itself for login shells; sourcing it here
        # runs profile.d twice and duplicates PATH entries.
        self.assertNotIn("if [ -r /etc/profile ]", profile)

        bashrc = heredoc(spec, "/etc/skel/.bashrc")
        self.assertIn(". /etc/profile.d/bash_completion.sh", bashrc)
        # Re-sourcing all of /etc/profile.d appends to PATH in some snippets.
        self.assertNotIn("/etc/profile.d/*.sh", bashrc)


if __name__ == "__main__":
    unittest.main()
