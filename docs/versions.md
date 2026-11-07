# Version policy and package synchronisation

The base package set is pinned in [`tenko.lock`](../tenko.lock).  The rule,
including how to handle packages outside the base set, is in
[`AGENTS.md`](../AGENTS.md) — this page only describes the tooling.

## The rule in one line

Every base package we build or install must be **at least** the version pinned
in `tenko.lock`, including its dependency chain.  If a package is not in
`tenko.lock`, stop and ask before choosing a version or substitute.

## Distro release and package versions

The distribution release is **Tenko 6 (Workstation)**.  `tenko-release`
carries the release identity and is versioned `6-2`.  Upstream packages roll
independently and keep their own versions; the `tenko-*` glue packages track
the distro release and are rebased as a group (`Epoch: 1` keeps older
`13.1-*` installs upgradable).  The distro release is not the version of
every package.

`/etc/os-release`:

```ini
NAME="Tenko Linux"
ID=tenko
VERSION="6 (Workstation)"
VERSION_ID="6"
PRETTY_NAME="Tenko Linux 6 (Workstation)"
VARIANT="Workstation"
VARIANT_ID=workstation
RELEASE_TYPE=stable
```

The distro repository is `tenko-6`:
`/etc/yum.repos.d/tenko-6.repo`, id `tenko-6`, at
<https://tenko.pjfox.xyz/packages/6/>.  It is the only repository file the
release package ships.

## Upgrading from the 13.1 packages

No Browneye compatibility aliases are shipped.  The `tenko-*` glue packages
carry `Epoch: 1`, so `dnf upgrade` replaces an installed `13.1-*` glue
package with the `6-*` build even though the version number is lower.

## `tenko.lock`

`tenko.lock` pins the base package set: package names, versions, hashes, the
build order and aliases for packages whose spec name differs
(`pcre` → `pcre2`, `libelf` → `elfutils`, …).

## Syncing a spec

`sync_lock_spec.py` reads `tenko.lock` and is **report-only** by default:

```sh
python3 scripts/sync_lock_spec.py                  # show work
python3 scripts/sync_lock_spec.py --write          # apply mechanical parts
```

With `--write` it bumps `Version:`, updates the `sources` line (md5 + URL),
updates `Source0`, and prepends a changelog entry.  It deliberately does not
touch configure options, patches or `%files`; anything else is printed for a
manual pass.

Always review the report: a version bump often needs a build-option or patch
change that the script cannot infer.

## Regenerating the base meta-package

`tenko-base` requires every package in the pinned base set.  After changing
`tenko.lock` or `package_specs/tenko-base/requires-extra`, regenerate the
Requires block:

```sh
scripts/gen_base_requires.py            # rewrite the spec in place
scripts/gen_base_requires.py --check    # exit 1 if the block is stale
```

## Rebuild order

When a spec changes:

1. bump `Version`/`Release` and the changelog,
2. rebuild it (`docs/build.md`),
3. publish it to both sites (`docs/build.md`; never only one),
4. rebuild and publish anything that depends on it.

Approved deviations (packages above the pinned version, packages outside the
base set built from latest upstream, retired specs) are recorded in the Gitea
issues, principally #7.  Do not silently add a new one.
