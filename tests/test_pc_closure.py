"""tenko-builddep installs the pkg-config closure of the BuildRequires (#62).

.pc Requires are not RPM requirements (macros.tenko), so the builder must
install the packages a declared library's .pc files name.  The helper runs
here against fake rpm/dnf/pkgconfigdeps commands backed by a small package
universe.
"""
import json
import os
import stat
import subprocess
import tempfile
import textwrap
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(REPO_ROOT, "package_specs", "tenko-rpm-config")
HELPER = os.path.join(CONFIG, "files", "tenko-builddep")

# name -> (.pc modules it ships, .pc modules those files require)
UNIVERSE = {
    "gtk+": (["gtk+-3.0"], ["gdk-pixbuf-2.0", "x11"]),
    "gdk-pixbuf": (["gdk-pixbuf-2.0"], ["shared-mime-info"]),
    "shared-mime-info": (["shared-mime-info"], []),
    "libx11": (["x11"], ["xproto", "nonexistent"]),
    "xorgproto": (["xproto"], []),
    "unrelated": (["unrelated"], []),
}

FAKE = textwrap.dedent('''\
    #!/usr/bin/env python3
    import json, os, sys
    state = os.environ["FAKE_STATE"]
    universe = json.load(open(os.path.join(state, "universe.json")))
    installed_file = os.path.join(state, "installed")
    installed = open(installed_file).read().split()
    tool, args = os.path.basename(sys.argv[0]), sys.argv[1:]

    def providers(cap, pool):
        cap = cap.split()[0]
        if cap.startswith("pkgconfig(") and cap.endswith(")"):
            mod = cap[len("pkgconfig("):-1]
            return [n for n in pool if mod in universe[n][0]]
        return [cap] if cap in pool else []

    if tool == "rpm" and "-ql" in args:
        for mod in universe[args[-1]][0]:
            print("/usr/lib64/pkgconfig/%s.pc" % mod)
    elif tool == "rpm":
        found = providers(args[-1], installed)
        if not found:
            print("no package provides " + args[-1]); sys.exit(1)
        print("\\n".join(found))
    elif tool == "dnf":
        caps = args[args.index("install") + 1:]
        with open(os.path.join(state, "dnf.log"), "a") as log:
            log.write(" ".join(caps) + "\\n")
        for cap in caps:
            for name in providers(cap, list(universe)):
                if name not in installed:
                    installed.append(name)
        open(installed_file, "w").write("\\n".join(installed))
    elif tool == "pkgconfigdeps":
        for line in sys.stdin:
            mod = os.path.basename(line.strip())[:-3]
            for name, (mods, reqs) in universe.items():
                if mod in mods:
                    for req in reqs:
                        print("pkgconfig(%s) " % req)
''')


class PcClosureTest(unittest.TestCase):
    def run_helper(self, installed, *caps):
        state = tempfile.mkdtemp()
        self.addCleanup(subprocess.run, ["rm", "-rf", state])
        with open(os.path.join(state, "universe.json"), "w") as handle:
            json.dump(UNIVERSE, handle)
        with open(os.path.join(state, "installed"), "w") as handle:
            handle.write("\n".join(installed))
        for tool in ("rpm", "dnf", "pkgconfigdeps"):
            path = os.path.join(state, tool)
            with open(path, "w") as handle:
                handle.write(FAKE)
            os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        env = dict(os.environ, FAKE_STATE=state,
                   PATH=state + os.pathsep + os.environ["PATH"],
                   TENKO_PKGCONFIGDEPS=os.path.join(state, "pkgconfigdeps"))
        result = subprocess.run(["bash", HELPER, "--opt", "--", *caps], env=env,
                                capture_output=True, text=True, timeout=60)
        with open(os.path.join(state, "installed")) as handle:
            return result, set(handle.read().split())

    def test_installs_transitive_pc_requires(self):
        result, installed = self.run_helper(["gtk+"], "gtk+ >= 3.24")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(installed, {"gtk+", "gdk-pixbuf", "shared-mime-info",
                                     "libx11", "xorgproto"})
        # A module nothing provides is reported, not fatal.
        self.assertIn("no package provides pkgconfig(nonexistent)", result.stderr)

    def test_ignores_packages_outside_the_closure(self):
        _, installed = self.run_helper(["xorgproto"], "xorgproto")
        self.assertEqual(installed, {"xorgproto"})


class PcClosureWiringTest(unittest.TestCase):
    def test_builder_runs_the_helper(self):
        with open(os.path.join(REPO_ROOT, "scripts", "build", "in_container.sh")) as handle:
            self.assertIn("/specs/tenko-rpm-config/files/tenko-builddep", handle.read())

    def test_rpm_config_ships_the_helper(self):
        with open(os.path.join(CONFIG, "files", "tenko-rpm-config.filelist")) as handle:
            self.assertIn("%{_bindir}/tenko-builddep", handle.read().split())

    def test_pc_requires_stay_out_of_runtime_packages(self):
        with open(os.path.join(CONFIG, "files", "macros.tenko")) as handle:
            self.assertIn("%__requires_exclude_from ^%{_libdir}/pkgconfig/", handle.read())


if __name__ == "__main__":
    unittest.main()
