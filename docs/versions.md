# Version policy and base manifest

The base package set is defined in
[`package_specs/base.json`](../package_specs/base.json).  The policy is in
[`AGENTS.md`](../AGENTS.md) — this page describes the manifest and tooling.

## Policy in one line

Packages track the latest stable upstream release.  Record the version and the
basis in the `%changelog`; source URLs and hashes live in the package's
`sources` file.  There is no global version lock.

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

## `package_specs/base.json`

The manifest has three keys:

- `packages` — base membership.  `tenko-base` requires exactly this set plus
  `package_specs/tenko-base/requires-extra`.
- `aliases` — base name → spec directory when they differ (`pcre` → `pcre2`,
  `libelf` → `elfutils`, …).
- `build_order` — the order used to rebuild the base set; it includes
  bootstrap extras and the tenko glue packages.

Each package's `package_specs/<name>/sources` file is the only source URL and
hash data.  A version bump updates the spec and that file; nothing else pins
the version.  Historical changelog entries may mention the retired
`tenko.lock`; that file no longer exists.

## Regenerating the base meta-package

`tenko-base` requires every package in `base.json["packages"]`.  After
changing `base.json` or `package_specs/tenko-base/requires-extra`, regenerate
the Requires block:

```sh
./tenko base-requires            # rewrite the spec in place
./tenko base-requires --check    # exit 1 if the block is stale
```

## Rebuild order

When a spec changes:

1. update `Version`/`Release`, the `sources` file and the changelog,
2. rebuild it (`docs/build.md`),
3. publish it to both sites (`docs/build.md`; never only one),
4. rebuild and publish anything that depends on it.

Non-latest versions, substitutes and retired specs are approved exceptions and
are recorded in the Gitea issues, principally #7.  Do not silently add one.
