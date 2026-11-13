#!/usr/bin/env python3
"""Regenerate the vendored Rust/Go dependency bundle of a package.

rpmbuild runs with --network=none, so a Rust or Go package carries its
dependencies as a separate source, <name>-<version>-vendor.tar.xz.  A
package that has one keeps a `vendor` marker next to its spec:

    # comments and blank lines are ignored
    kind      cargo | go
    tree      FILE   upstream tarball to vendor (default: first sources line)
    lockfile  FILE   a sources file copied over Cargo.lock first (optional)

`tenko vendor PKG` unpacks the tree in the buildroot image, installs the
distro toolchain (rust or go) and CA certificates (make-ca) from the local
repositories, runs
`cargo vendor --locked` or `go mod vendor` with network access and packs
vendor/ deterministically: sorted entries, mtime 0, root owner, normalised
modes, GNU tar format, `xz -T1`.  The same inputs and toolchain give the
same md5.  The bundle goes into the sources cache and the package's
`sources` line is rewritten to its hosted URL,
$PUBLIC_URL/sources/<pkg>/<file>.  Upload it with `tenko publish sources`.

Usage:
    tenko vendor gh restic           # regenerate and record
    tenko vendor --check gh          # regenerate, compare with sources
    tenko vendor --all --check       # every package with a marker

The mirror cache is synced first (`tenko sync`) so the newest toolchain
is used; OFFLINE=1 skips that.

Environment: OFFLINE, BUILDROOT_IMAGE (container image), PUBLIC_URL,
TENKO_SOURCES_DIR, TENKO_REPO_CACHE, TENKO_LOCAL_REPO.
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fetch_sources  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
SPECS_DIR = os.path.join(REPO_ROOT, "package_specs")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://tenko.pjfox.xyz").rstrip("/")
SOURCES_DIR = fetch_sources.DEFAULT_SOURCES_DIR
REPO_CACHE = os.environ.get(
    "TENKO_REPO_CACHE", os.path.join(REPO_ROOT, "build", "cache", "repo"))
LOCAL_REPO = os.environ.get(
    "TENKO_LOCAL_REPO", os.path.join(REPO_ROOT, "build", "repo"))
IMAGE = os.environ.get("BUILDROOT_IMAGE", "localhost/tenko/buildroot:r6")

KINDS = {"cargo": "rust", "go": "go"}
KEYS = ("kind", "tree", "lockfile")

# Runs inside the container as root.  Arguments: kind, tree, lockfile
# (may be empty), output file name.
CONTAINER_SCRIPT = r"""
set -eu
umask 022
kind=$1 tree=$2 lockfile=$3 out=$4
dnf -y -q --disablerepo='*' --nogpgcheck \
    --repofrompath=local,file:///repo/local \
    --repofrompath=cache,file:///repo/cache \
    --setopt=install_weak_deps=False install "$5" make-ca >/dev/null
mkdir /w
tar -xf "/src/$tree" -C /w
set -- /w/*
[ $# -eq 1 ] && [ -d "$1" ] || { echo "error: $tree has no single top directory" >&2; exit 1; }
cd "$1"
rm -rf vendor
[ -n "$lockfile" ] && cp "/src/$lockfile" Cargo.lock
case $kind in
cargo)
    export PATH=/opt/rust/bin:$PATH CARGO_HOME=/tmp/cargo-home
    cargo vendor --locked --quiet vendor >/dev/null
    ;;
go)
    export GOTOOLCHAIN=local GOFLAGS=-mod=mod GOMODCACHE=/tmp/gomod \
        GOCACHE=/tmp/gocache GOPROXY=https://proxy.golang.org,direct \
        GOSUMDB=sum.golang.org
    go mod vendor
    ;;
esac
[ -d vendor ] || { echo "error: no vendor/ directory was produced" >&2; exit 1; }
tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
    --mode=u+rw,go+r,go-w,a+X --format=gnu -cf - vendor | xz -T1 -6 >"/out/$out"
"""


def read_marker(pkg):
    path = os.path.join(SPECS_DIR, pkg, "vendor")
    marker = {}
    with open(path, encoding="utf-8") as handle:
        for lineno, raw in enumerate(handle, start=1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            fields = line.split()
            if len(fields) != 2 or fields[0] not in KEYS:
                raise ValueError("{}:{}: expected 'KEY VALUE' with KEY in {}"
                                 .format(path, lineno, ", ".join(KEYS)))
            marker[fields[0]] = fields[1]
    if marker.get("kind") not in KINDS:
        raise ValueError("{}: kind must be one of {}".format(path, ", ".join(KINDS)))
    return marker


def marked_packages():
    return sorted(name for name in os.listdir(SPECS_DIR)
                  if os.path.isfile(os.path.join(SPECS_DIR, name, "vendor")))


def name_version(pkg):
    spec = os.path.join(SPECS_DIR, pkg, pkg + ".spec")
    out = subprocess.run(
        ["rpmspec", "-q", "--srpm", "--qf", "%{name}-%{version}\n", spec],
        check=True, capture_output=True, text=True).stdout.split()
    return out[0]


def bundle_name(pkg):
    return name_version(pkg) + "-vendor.tar.xz"


def bundle_url(pkg, filename):
    return "{}/sources/{}/{}".format(PUBLIC_URL, pkg, filename)


def md5sum(path):
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_bundle_line(source, pkg, filename):
    name = fetch_sources.source_filename(source)
    return name == filename or name.endswith("-vendor.tar.xz") or \
        name.endswith("-vendor.tar.gz") or \
        source[1].startswith(PUBLIC_URL + "/sources/" + pkg + "/")


def generate(pkg, workdir):
    marker = read_marker(pkg)
    sources_file = os.path.join(SPECS_DIR, pkg, "sources")
    sources = fetch_sources.parse_sources(sources_file)
    filename = bundle_name(pkg)
    inputs = [s for s in sources if not is_bundle_line(s, pkg, filename)]
    if not inputs:
        raise ValueError("{}: no upstream source to vendor".format(sources_file))
    by_name = {fetch_sources.source_filename(s): s for s in inputs}
    tree = marker.get("tree", fetch_sources.source_filename(inputs[0]))
    lockfile = marker.get("lockfile", "")
    for needed in filter(None, (tree, lockfile)):
        if needed not in by_name:
            raise ValueError("{}: {} is not a sources entry".format(sources_file, needed))
    wanted = [by_name[n] for n in filter(None, (tree, lockfile))]
    if not fetch_sources.fetch_sources(wanted, SOURCES_DIR):
        raise RuntimeError("could not fetch the sources of " + pkg)

    os.makedirs(LOCAL_REPO, exist_ok=True)
    srcdir = os.path.join(workdir, "src")
    outdir = os.path.join(workdir, "out")
    os.makedirs(srcdir)
    os.makedirs(outdir)
    for name in filter(None, (tree, lockfile)):
        fetch_sources.link_or_copy(os.path.join(SOURCES_DIR, name),
                                   os.path.join(srcdir, name))
    print("vendoring {} ({}) from {}".format(pkg, marker["kind"], tree))
    subprocess.run(
        ["podman", "run", "--rm", "--network=host",
         "-v", srcdir + ":/src:ro,z", "-v", outdir + ":/out:rw,z",
         "-v", REPO_CACHE + ":/repo/cache:ro,z",
         "-v", LOCAL_REPO + ":/repo/local:ro,z",
         IMAGE, "sh", "-c", CONTAINER_SCRIPT, "vendor",
         marker["kind"], tree, lockfile, filename, KINDS[marker["kind"]]],
        check=True)
    return filename, os.path.join(outdir, filename), sources


def record(pkg, filename, path, sources):
    md5 = md5sum(path)
    os.makedirs(SOURCES_DIR, exist_ok=True)
    dest = os.path.join(SOURCES_DIR, filename)
    shutil.copyfile(path, dest + ".part")
    os.replace(dest + ".part", dest)
    line = "{} {}".format(md5, bundle_url(pkg, filename))
    sources_file = os.path.join(SPECS_DIR, pkg, "sources")
    with open(sources_file, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    out, replaced = [], False
    for raw in lines:
        fields = raw.split()
        if raw.strip() and not raw.lstrip().startswith("#") and \
                is_bundle_line([fields[0], fields[1], fields[2] if len(fields) > 2 else None],
                               pkg, filename):
            if not replaced:
                out.append(line)
                replaced = True
            continue
        out.append(raw)
    if not replaced:
        out.append(line)
    with open(sources_file, "w", encoding="utf-8") as handle:
        handle.write("\n".join(out) + "\n")
    print("  {}  {}".format(md5, filename))
    print("  recorded in {}".format(os.path.relpath(sources_file, REPO_ROOT)))


def check(pkg, filename, path, sources):
    md5 = md5sum(path)
    recorded = [s[0] for s in sources
                if fetch_sources.source_filename(s) == filename]
    if recorded and recorded[0] == md5:
        print("  reproducible: {}  {}".format(md5, filename))
        return True
    print("  MISMATCH: {} regenerates as {}, sources records {}".format(
        filename, md5, recorded[0] if recorded else "nothing"))
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("packages", nargs="*", help="package directory names")
    parser.add_argument("--all", action="store_true",
                        help="every package with a vendor marker")
    parser.add_argument("--check", action="store_true",
                        help="regenerate and compare; change nothing")
    args = parser.parse_args(argv)
    packages = marked_packages() if args.all else args.packages
    if not packages:
        parser.error("name packages or pass --all")

    if os.environ.get("OFFLINE", "0") != "1":
        subprocess.run(["bash", os.path.join(HERE, "sync.sh")], check=True)

    ok = True
    for pkg in packages:
        pkg = pkg.strip("/").split("/")[-1].removesuffix(".spec")
        with tempfile.TemporaryDirectory(prefix="tenko-vendor-") as workdir:
            try:
                filename, path, sources = generate(pkg, workdir)
            except subprocess.CalledProcessError as exc:
                print("error: {}: the vendor container failed (exit {})".format(
                    pkg, exc.returncode), file=sys.stderr)
                ok = False
                continue
            except (OSError, ValueError, RuntimeError) as exc:
                print("error: {}: {}".format(pkg, exc), file=sys.stderr)
                ok = False
                continue
            if args.check:
                ok = check(pkg, filename, path, sources) and ok
            else:
                record(pkg, filename, path, sources)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
