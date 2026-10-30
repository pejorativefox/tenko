#!/usr/bin/env python3
"""Generate lfs.lock from an LFS book checkout.

Pins a tag of the LFS book and extracts:

  * the package versions from packages.ent
  * the base package list from chapter08/chapter08.xml (systemd variant)
  * the patch list (file name, md5, size, download URL) from patches.ent
  * the LFS <-> browneye spec aliases

The output is deterministic JSON: no timestamps are written, so re-running for
the same tag produces byte-identical output.
"""

import argparse
import json
import os
import re
import subprocess
import sys

# Pages under chapter08 that are not packages.
CHAPTER08_NON_PACKAGES = {
    "chapter08",
    "introduction",
    "pkgmgt",
    "aboutdebug",
    "stripping",
    "cleanup",
}

# Included by chapter08.xml but only for the sysvinit book variant.
SYSV_ONLY = {"udev", "sysklogd", "sysvinit"}

# Entity names that end in "-version" but are not package versions.
VERSION_ENTITY_BLOCKLIST = {
    "version",
    "short-version",
    "generic-version",
    "generic-versiond",
    "blfs-version",
}

# Some packages publish their sources under a different entity prefix.
SOURCE_NAME_FALLBACKS = {
    "pcre": ["pcre2"],
    "libelf": ["elfutils"],
    "procps": ["procps-ng"],
}

# browneye spec directory for LFS package names that do not match 1:1.
DEFAULT_ALIASES = {
    "pcre": "pcre2",
    "procps": "procps-ng",
    "libelf": "elfutils",
    "flit-core": "python-flit-core",
    "packaging": "python-packaging",
    "wheel": "python-wheel",
    "setuptools": "python-setuptools",
    "jinja2": "python-jinja",
    "markupsafe": "python-markupsafe",
}

ENTITY_RE = re.compile(r'<!ENTITY\s+([A-Za-z0-9_.-]+)\s+"([^"]*)"\s*>')
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
REF_RE = re.compile(r"&([A-Za-z0-9_.-]+);")
INCLUDE_RE = re.compile(r'href="([A-Za-z0-9_.-]+)\.xml"')


def git_show(repo, tag, path):
    return subprocess.check_output(
        ["git", "-C", repo, "show", f"{tag}:{path}"], text=True
    )


def strip_comments(text):
    return COMMENT_RE.sub("", text)


def parse_entities(text):
    """Parse <!ENTITY name "value"> definitions. Parameter entities are skipped.

    Duplicate names are resolved last-wins. The book redefines a few entities in
    mutually exclusive conditional sections; for our purposes the last
    definition (the fully expanded one, e.g. linux-version with the patch
    level) is the useful one.
    """
    entities = {}
    for name, value in ENTITY_RE.findall(strip_comments(text)):
        entities[name] = value
    return entities


def resolve(value, entities, max_passes=20):
    for _ in range(max_passes):
        new = REF_RE.sub(lambda m: entities.get(m.group(1), m.group(0)), value)
        if new == value:
            break
        value = new
    return value


def resolve_all(entities):
    return {name: resolve(value, entities) for name, value in entities.items()}


def package_versions(resolved):
    packages = {}
    for name, value in resolved.items():
        if not name.endswith("-version"):
            continue
        if name in VERSION_ENTITY_BLOCKLIST:
            continue
        if "&" in value or "%" in value or not value:
            continue
        packages[name[: -len("-version")]] = value
    return packages


def base_packages(repo, tag):
    chapter = strip_comments(git_show(repo, tag, "chapter08/chapter08.xml"))
    names = []
    for name in INCLUDE_RE.findall(chapter):
        if name in CHAPTER08_NON_PACKAGES or name in SYSV_ONLY:
            continue
        names.append(name)
    return names


def canonical_name(resolved, name):
    """Return the entity name that actually defines the package version."""
    for candidate in [name] + SOURCE_NAME_FALLBACKS.get(name, []):
        if "{}-version".format(candidate) in resolved:
            return candidate
    return name


def package_sources(resolved, packages):
    """Return the main source URL/md5 for packages that publish one."""
    sources = {}
    for name in packages:
        canonical = canonical_name(resolved, name)
        url = resolved.get("{}-url".format(canonical))
        md5 = resolved.get("{}-md5".format(canonical))
        if not url or not md5:
            continue
        if not re.fullmatch(r"[0-9a-f]{32}", md5):
            continue
        if "&" in url or "%" in url:
            continue
        url = url.replace("github.com//", "github.com/")
        sources[canonical] = {
            "url": url,
            "md5": md5,
            "size": resolved.get("{}-size".format(canonical), ""),
        }
    return sources


def patches(repo, tag, resolved, patches_base):
    found = {}
    for name, value in resolved.items():
        if not name.endswith("-patch"):
            continue
        if "&" in value:
            continue
        md5 = resolved.get(f"{name}-md5")
        size = resolved.get(f"{name}-size")
        if not md5 or not re.fullmatch(r"[0-9a-f]{32}", md5):
            continue
        found[name] = {
            "file": value,
            "md5": md5,
            "size": size or "",
            "url": patches_base + value,
        }
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lfs-repo",
        default=os.environ.get("LFS_REPO", os.path.expanduser("~/repos/lfs")),
        help="path to the LFS book git checkout (default: ~/repos/lfs)",
    )
    parser.add_argument("--tag", default="r13.1", help="LFS tag to pin")
    parser.add_argument(
        "--output", default="lfs.lock", help="output file (default: lfs.lock)"
    )
    args = parser.parse_args()

    repo = os.path.abspath(os.path.expanduser(args.lfs_repo))
    if not os.path.isdir(os.path.join(repo, ".git")):
        sys.exit(f"error: {repo} is not a git checkout")

    try:
        commit = subprocess.check_output(
            ["git", "-C", repo, "rev-parse", args.tag], text=True
        ).strip()
        commit_date = subprocess.check_output(
            ["git", "-C", repo, "show", "-s", "--format=%cI", args.tag], text=True
        ).strip()
    except subprocess.CalledProcessError:
        sys.exit(f"error: tag {args.tag!r} not found in {repo}")

    general_ent = parse_entities(git_show(repo, args.tag, "general.ent"))
    packages_ent = parse_entities(git_show(repo, args.tag, "packages.ent"))
    patches_ent = parse_entities(git_show(repo, args.tag, "patches.ent"))

    # Patch file names reference package versions (coreutils-&coreutils-version;),
    # so resolve both entity sets together.
    all_entities = {**general_ent, **packages_ent, **patches_ent}
    resolved = resolve_all(all_entities)
    resolved_packages = resolved
    resolved_patches = resolved

    release = args.tag.lstrip("r")
    patches_base = f"https://www.linuxfromscratch.org/patches/lfs/{release}/"

    lock = {
        "lfs": {
            "tag": args.tag,
            "commit": commit,
            "commit_date": commit_date,
            "repo": "https://git.linuxfromscratch.org/lfs.git",
        },
        "variant": "systemd",
        "base_packages": base_packages(repo, args.tag),
        "aliases": DEFAULT_ALIASES,
        "packages": package_versions(resolved_packages),
        "canonical_names": {
            name: canonical_name(resolved_packages, name)
            for name in base_packages(repo, args.tag)
        },
        "sources": package_sources(resolved_packages, base_packages(repo, args.tag)),
        "patches": patches(repo, args.tag, resolved_patches, patches_base),
    }

    text = json.dumps(lock, indent=2, sort_keys=True) + "\n"
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(text)

    print(f"wrote {args.output}")
    print(f"  lfs {args.tag} ({commit[:12]})")
    print(f"  base packages: {len(lock['base_packages'])}")
    print(f"  versions:      {len(lock['packages'])}")
    print(f"  patches:       {len(lock['patches'])}")


if __name__ == "__main__":
    main()
