#!/usr/bin/env python3
"""Suggest BuildRequires a spec is missing (issue #58).

Two kinds of evidence, mapped to packages through the offline mirror:

  * the package's built RPMs: their automatic Requires (shared libraries,
    pkgconfig(...), perl(...), interpreters) name what the build linked
    against or installed scripts for.  By default the newest RPMs in
    build/repo or the mirror are used, so nothing has to be built first.
  * a build log (`--out OUT` reads OUT/logs/<pkg>.log): pkg-config, meson,
    CMake, missing commands and missing Perl modules.  Run a STRICT=1 build
    first to get a log that shows what the buildroot lacks.

Packages already in the buildroot (tenko-buildroot's closure), already
declared, or built from the spec itself are left out.  The output is a list
of BuildRequires lines with the evidence for each, for review; specs are
never edited.

Usage:
    tenko builddeps xsetroot
    STRICT=1 OUT=build/x tenko build xsetroot; tenko builddeps --out build/x xsetroot
"""

import argparse
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPECS = os.path.join(ROOT, "package_specs")
CACHE = os.environ.get("TENKO_REPO_CACHE", os.path.join(ROOT, "build", "cache", "repo"))
LOCAL = os.environ.get("TENKO_LOCAL_REPO", os.path.join(ROOT, "build", "repo"))
BUILD_IMAGE = os.environ.get("BUILD_IMAGE", "localhost/tenko/build:r6")
BUILDROOT_IMAGE = os.environ.get("BUILDROOT_IMAGE", "localhost/tenko/buildroot:r6")

# (regex, capability template, label).  Optional meson dependencies that
# were not found are reported too: they are the silently dropped features.
LOG_PATTERNS = [
    (r"Package '([^']+)',? (?:required by '[^']*', )?not found", "pkgconfig({})", "pkg-config"),
    (r"No package '([^']+)' found", "pkgconfig({})", "pkg-config"),
    (r'Dependency "?([\w.+-]+)"? (?:\(tried [^)]*\) )?not found', "pkgconfig({})", "meson"),
    (r"(?:Run-time|Build-time) dependency ([\w.+-]+) found: NO", "pkgconfig({})", "meson (optional)"),
    (r"ERROR: Program '([\w.+-]+)' not found", "/usr/bin/{}", "meson program"),
    (r"^Program ([\w.+-]+) found: NO", "/usr/bin/{}", "meson program (optional)"),
    (r'Could not find a package configuration file provided by "([\w.+-]+)"', "cmake({})", "cmake"),
    (r"Could NOT find ([\w.+-]+)", "pkgconfig({})", "cmake FindPackage"),
    (r"(?:^|\s)([\w.+-]+): (?:command )?not found", "/usr/bin/{}", "command"),
    (r"/usr/bin/env: '([\w.+-]+)': No such file", "/usr/bin/{}", "command"),
    (r"Can't locate ([\w/]+)\.pm in @INC", "perl({})", "perl module"),
    (r"No module named '([\w.]+)'", "python:{}", "python module"),
    (r"python3? -c 'import ([\w.]+)[;']", "python:{}", "python module"),
    (r"python3? is missing modules: ([\w.]+)", "python:{}", "python module"),
    (r"Cannot import '([\w.]+)'", "python:{}", "python build backend"),
]


PYTHON_PACKAGES = {"jinja2": "python-jinja", "yaml": "python-pyyaml",
                   "flit_core": "python-flit-core", "elftools": "python3-pyelftools"}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw).stdout


def spec_for(name):
    name = name[len("package_specs/"):] if name.startswith("package_specs/") else name
    if name.endswith(".spec"):
        path = os.path.join(SPECS, name)
    else:
        name = name.rstrip("/")
        path = os.path.join(SPECS, name, name + ".spec")
    if not os.path.isfile(path):
        sys.exit("missing spec: " + name)
    return path


def spec_query(spec, *args):
    return [l for l in run(["rpmspec", "-q", *args, spec]).splitlines() if l.strip()]


def newest_rpms(names):
    """Newest RPM file per binary package name from build/repo or the mirror."""
    found = []
    for name in names:
        best = None
        for repo in (LOCAL, CACHE):
            for path in glob.glob(os.path.join(repo, glob.escape(name) + "-*.rpm")):
                base = os.path.basename(path)
                # name-version-release.arch.rpm; the version starts with a digit.
                if re.match(re.escape(name) + r"-\d", base):
                    if best is None or os.path.getmtime(path) > os.path.getmtime(best):
                        best = path
        if best:
            found.append(best)
    return found


def rpm_caps(rpms, own):
    caps = {}
    for rpm in rpms:
        for req in run(["rpm", "-qp", "--requires", rpm]).splitlines():
            cap = req.split(" ")[0]
            if cap.startswith(("rpmlib(", "config(")) or cap in own:
                continue
            if ".so" in cap or cap.startswith(("pkgconfig(", "perl(", "/")):
                caps.setdefault(cap, set()).add("rpm requires")
    return caps


def log_caps(log):
    caps, hints = {}, set()
    with open(log, errors="replace") as handle:
        text = handle.read()
    for pattern, template, label in LOG_PATTERNS:
        for match in re.finditer(pattern, text, re.M):
            name = match.group(1)
            if template is None:
                hints.add("{}: {}".format(label, name))
                continue
            if template == "python:{}":
                # Tenko has no python3dist() provides; packages are named
                # python-<module> (with a few renames).
                module = name.split(".")[0]
                name = PYTHON_PACKAGES.get(module, "python-" + module.replace("_", "-"))
                caps.setdefault(name, set()).add(label)
                continue
            if label == "perl module":
                name = name.replace("/", "::")
            if label == "cmake FindPackage":
                name = name.lower()
                # FindSWIG, FindPerl, ... look for a program, not a library.
                caps.setdefault("/usr/bin/" + name, set()).add(label)
            caps.setdefault(template.format(name), set()).add(label)
            if template == "/usr/bin/{}":
                caps.setdefault("/usr/sbin/" + name, set()).add(label)
    for match in re.finditer(r"configure: error: (.+)", text):
        hints.add("configure: " + match.group(1).strip())
    return caps, hints


def resolve(caps):
    """Map each capability to its providers with dnf in the build image."""
    if not caps:
        return {}
    script = r'''
while IFS= read -r cap; do
  for p in $(dnf -q --disablerepo='*' --repofrompath=local,file:///repo/local \
             --repofrompath=cache,file:///repo/cache repoquery --qf '%{name}' \
             --whatprovides "$cap" 2>/dev/null | sort -u); do
    printf '%s\t%s\n' "$cap" "$p"
  done
done
'''
    mounts = ["-v", CACHE + ":/repo/cache:ro,z"]
    mounts += ["-v", (LOCAL if os.path.isdir(os.path.join(LOCAL, "repodata"))
                      else CACHE) + ":/repo/local:ro,z"]
    out = run(["podman", "run", "--rm", "-i", "--network=none", *mounts,
               BUILD_IMAGE, "bash", "-c", script], input="\n".join(caps) + "\n")
    providers = {}
    for line in out.splitlines():
        cap, pkg = line.split("\t")
        providers.setdefault(cap, set()).add(pkg)
    return providers


def buildroot_packages():
    out = run(["podman", "run", "--rm", "--network=none", BUILDROOT_IMAGE,
               "rpm", "-qa", "--qf", "%{name}\n"])
    return set(out.split())


def main():
    parser = argparse.ArgumentParser(
        prog="tenko builddeps", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("packages", nargs="+", help="package dirs or spec paths")
    parser.add_argument("--out", help="a `tenko build` OUT directory: use its "
                        "logs and RPMs as evidence")
    args = parser.parse_args()

    baseline = buildroot_packages()
    status = 0
    for name in args.packages:
        spec = spec_for(name)
        pkg = os.path.basename(spec)[:-len(".spec")]
        own = set(spec_query(spec, "--qf", "%{name}\n"))
        declared_caps = [r.split(" ")[0] for r in spec_query(spec, "--buildrequires")]

        rpms, caps, hints = [], {}, set()
        if args.out:
            rpms = glob.glob(os.path.join(args.out, "build", pkg, "RPMS", "*", "*.rpm"))
            log = os.path.join(args.out, "logs", pkg + ".log")
            if os.path.isfile(log):
                caps, hints = log_caps(log)
        if not rpms:
            rpms = newest_rpms(sorted(own))
        for cap, sources in rpm_caps(rpms, own).items():
            caps.setdefault(cap, set()).update(sources)

        providers = resolve(sorted(set(caps) | set(declared_caps)))
        # A soname provided by a split <name>-libs package means the build
        # needed <name> too: the headers and .pc files live there.
        headers = {}
        for cap in caps:
            for provider in providers.get(cap, ()):
                if ".so" in cap and provider.endswith("-libs"):
                    headers.setdefault(provider[:-len("-libs")], set()).add(cap)
        for base, base_providers in resolve(sorted(headers)).items():
            for cap in headers[base]:
                caps[cap] = caps[cap] | {"headers: " + base}
                providers[cap] = providers.get(cap, set()) | base_providers
        declared = set()
        for cap in declared_caps:
            declared.add(cap)
            declared |= providers.get(cap, set())

        suggestions, unresolved = {}, []
        for cap, sources in sorted(caps.items()):
            found = providers.get(cap, set()) - own
            if not found:
                twin = cap.replace("/usr/bin/", "/usr/sbin/", 1)
                if twin != cap and providers.get(twin):
                    continue
                if cap.startswith("/usr/sbin/"):
                    continue  # reported once, as its /usr/bin twin
                if "rpm requires" not in sources:
                    unresolved.append("{} ({})".format(cap, ", ".join(sorted(sources))))
                continue
            # A -libs package in the buildroot does not bring the headers;
            # only count the header package as present.
            wanted = {p for p in found if not p.endswith("-libs")} or found
            if wanted & (baseline | declared):
                continue
            for provider in sorted(wanted - baseline - declared):
                suggestions.setdefault(provider, set()).add(
                    "{} [{}]".format(cap, ", ".join(sorted(sources))))

        with open(spec, encoding="utf-8", errors="replace") as handle:
            if re.search(r"^AutoReq:\s*(no|0)", handle.read(), re.M | re.I):
                hints.add("AutoReq is disabled: the RPMs carry no library "
                          "requirements, so only the build log is evidence")
        print("# {}: {} declared, evidence from {} RPM(s){}".format(
            pkg, len(declared_caps), len(rpms),
            " and the build log" if args.out else ""))
        for provider, why in sorted(suggestions.items()):
            print("BuildRequires: {:<28} # {}".format(provider, "; ".join(sorted(why))))
        for item in unresolved:
            print("#   unresolved: " + item)
        for hint in sorted(hints):
            print("#   hint: " + hint)
        if not suggestions:
            print("#   nothing missing found")
        else:
            status = 1
        print()
    return status


if __name__ == "__main__":
    sys.exit(main())
