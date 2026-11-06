#!/usr/bin/env python3
"""Sync a spec's Version/source URL with the pinned base release.

Reads tenko.lock, compares the spec's Version and Source0 with the pinned
base entry, and reports the work needed.

With --write it performs the mechanical parts only:

  * bumps ``Version:``
  * updates the matching line in the ``sources`` file (md5 + URL)
  * updates ``Source0`` when only the filename/extension changed
  * prepends a %changelog entry

Anything else (hardcoded old versions in %files, patches, configure changes)
is reported and must be handled by hand.
"""

import argparse
import datetime
import glob
import json
import os
import re
import sys

LOCK_PATH = "tenko.lock"
SPEC_GLOB = "package_specs/*/*.spec"

VERSION_RE = re.compile(r"^Version:\s*(\S+)\s*$", re.M)
SOURCE0_RE = re.compile(r"^Source0:\s*(.+?)\s*$", re.M)
ARCHIVE_RE = re.compile(r"\.(?:tar\.(?:gz|xz|bz2)|tgz|zip)$")


def load_lock(path=LOCK_PATH):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def spec_index():
    index = {}
    for spec in sorted(glob.glob(SPEC_GLOB)):
        name = os.path.basename(spec)[: -len(".spec")]
        index.setdefault(name, spec)
    return index


def reverse_aliases(lock):
    return {spec: base for base, spec in lock.get("aliases", {}).items()}


def expand(value, name, version):
    return (value
            .replace("%{name}", name)
            .replace("%{version}", version)
            .replace("%{_name}", name)
            .replace("%{_version}", version))


def read_lines(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read().splitlines()


def pick_source_line(lines, old_basename):
    candidates = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 2:
            continue
        candidates.append((idx, parts))
    for idx, parts in candidates:
        if os.path.basename(parts[1]) == old_basename:
            return idx, parts
    if len(candidates) == 1:
        return candidates[0]
    return None, None


def changelog_entry(version, note="Sync with the base set"):
    now = datetime.date.today()
    stamp = now.strftime("%a %b %d %Y")
    return "* {stamp} tenko <build@tenko.invalid> {version}\n- {note}".format(
        stamp=stamp, version=version, note=note)


def sync_one(name, lock, index, write=False, note="Sync with the base set"):
    aliases = reverse_aliases(lock)
    lock_name = lock.get("canonical_names", {}).get(name, name)
    if lock_name not in lock["packages"]:
        lock_name = name if name in lock["packages"] else aliases.get(name, name)
    if lock_name not in lock["packages"]:
        return {"name": name, "status": "unknown-package"}

    spec_name = lock["aliases"].get(name)
    if not spec_name or spec_name not in index:
        spec_name = name if name in index else lock["aliases"].get(lock_name, name)
    spec_path = index.get(spec_name)
    if spec_path is None:
        return {"name": name, "status": "no-spec"}

    new_version = lock["packages"][lock_name]
    if lock_name == "sqlite" and "sqlite-short" in lock["packages"]:
        new_version = lock["packages"]["sqlite-short"]
    source = lock.get("sources", {}).get(lock_name)
    spec_text = open(spec_path, "r", encoding="utf-8").read()

    match = VERSION_RE.search(spec_text)
    if not match:
        return {"name": name, "status": "no-version"}
    old_version = match.group(1)

    report = {
        "name": name,
        "lock_name": lock_name,
        "spec": spec_path,
        "old_version": old_version,
        "new_version": new_version,
        "source": source,
        "warnings": [],
        "status": "ok",
    }

    if old_version == new_version:
        report["status"] = "up-to-date"
        return report

    source0 = SOURCE0_RE.search(spec_text)
    source0_value = source0.group(1) if source0 else None
    old_basename = None
    new_basename = None
    new_source0 = None
    if source0_value:
        old_basename = os.path.basename(expand(source0_value, name, old_version))
        new_basename = os.path.basename(source["url"]) if source else None
        if new_basename:
            expected = os.path.basename(expand(source0_value, name, new_version))
            if expected == new_basename:
                new_source0 = source0_value
            elif old_basename and ARCHIVE_RE.sub("", old_basename) == ARCHIVE_RE.sub("", new_basename):
                extension = ARCHIVE_RE.search(new_basename).group(0)
                new_source0 = ARCHIVE_RE.sub(extension, source0_value)
            else:
                new_source0 = new_basename
                report["warnings"].append(
                    "Source0 will be replaced with the upstream filename")
    else:
        report["warnings"].append("no Source0 line")

    if source is None:
        report["warnings"].append("no source URL/md5 in tenko.lock")

    stale = [line.strip() for line in spec_text.splitlines()
             if old_version in line
             and not line.startswith("Version:")
             and not line.lstrip().startswith("*")
             and not line.lstrip().startswith("#")
             and "%changelog" not in line]
    if stale:
        report["warnings"].append(
            "old version appears in {} spec line(s): {}".format(
                len(stale), "; ".join(stale[:4])))

    report["source0_old"] = source0_value
    report["source0_new"] = new_source0
    report["old_basename"] = old_basename
    report["new_basename"] = new_basename

    if not write:
        report["status"] = "would-update"
        return report

    # --- write ---
    spec_text = VERSION_RE.sub("Version:    {}".format(new_version), spec_text, count=1)
    if new_source0 and source0_value != new_source0:
        spec_text = SOURCE0_RE.sub("Source0:    {}".format(new_source0), spec_text, count=1)
    if "%changelog" in spec_text:
        spec_text = spec_text.replace(
            "%changelog\n", "%changelog\n" + changelog_entry(new_version, note) + "\n\n", 1)

    if source and old_basename:
        sources_path = os.path.join(os.path.dirname(spec_path), "sources")
        if os.path.isfile(sources_path):
            lines = read_lines(sources_path)
            idx, parts = pick_source_line(lines, old_basename)
            if idx is not None:
                override = parts[2] if len(parts) > 2 else ""
                suffix = " " + override if override else ""
                lines[idx] = "{} {}{}".format(source["md5"], source["url"], suffix)
                with open(sources_path, "w", encoding="utf-8") as handle:
                    handle.write("\n".join(lines) + "\n")
            else:
                report["warnings"].append("could not find source line to update")

    with open(spec_path, "w", encoding="utf-8") as handle:
        handle.write(spec_text)
    report["status"] = "updated"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packages", nargs="*", help="spec names or base names")
    parser.add_argument("--write", action="store_true", help="apply changes")
    parser.add_argument("--all-base", action="store_true",
                        help="run over every base package in tenko.lock")
    parser.add_argument("--note", default="Sync with the base set",
                        help="changelog note")
    args = parser.parse_args()

    lock = load_lock()
    index = spec_index()

    targets = list(args.packages)
    if args.all_base or not targets:
        targets = lock["base_packages"]

    results = []
    for target in targets:
        results.append(sync_one(target, lock, index, write=args.write, note=args.note))

    width = max(len(r["name"]) for r in results) if results else 10
    for r in results:
        status = r["status"]
        if status in ("unknown-package", "no-spec", "no-version"):
            print("{:<{w}}  {}".format(r["name"], status, w=width))
            continue
        if status == "up-to-date":
            print("{:<{w}}  up-to-date ({})".format(r["name"], r["new_version"], w=width))
            continue
        print("{:<{w}}  {} -> {}  [{}]".format(
            r["name"], r["old_version"], r["new_version"], status, w=width))
        for warning in r["warnings"]:
            print("    ! {}".format(warning))

    changed = [r for r in results if r["status"] == "updated"]
    pending = [r for r in results if r["status"] == "would-update"]
    print("\n{} updated, {} would update, {} total".format(
        len(changed), len(pending), len(results)))


if __name__ == "__main__":
    main()
