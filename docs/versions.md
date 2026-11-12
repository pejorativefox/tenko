# Release identity and base manifest

The version policy (latest stable upstream, basis recorded in `%changelog`,
no global version lock) is in [`AGENTS.md`](../AGENTS.md); the bump and
rebuild procedure is in [`build.md`](build.md#version-bumps).  This page
describes the release identity and the base manifest.

## Distro release and package versions

The distribution release is **Tenko 6 (Workstation)**, carried by
`tenko-release` (version 6).  Upstream packages roll independently and keep
their own versions; the distro release is not the version of every package.
The `tenko-*` glue packages track the distro release, are rebased as a
group and carry `Epoch: 1`; keep the epoch when bumping them.

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
HOME_URL="https://tenko.pjfox.xyz/"
BUG_REPORT_URL="https://github.com/pejorativefox/tenko/issues"
SUPPORT_URL="https://github.com/pejorativefox/tenko"
DOCUMENTATION_URL="https://github.com/pejorativefox/tenko/tree/main/docs"
ANSI_COLOR="0;34"
```

`/etc/os-release` is a symlink to `/usr/lib/os-release`.  systemd reads the
URL fields for its SBAT metadata.

The distro repository is `tenko-6`: `/etc/yum.repos.d/tenko-6.repo`, id
`tenko-6`, at <https://tenko.pjfox.xyz/packages/6/>.  It is the only
repository file the release package ships.

## `package_specs/base.json`

The manifest has three keys:

- `packages` — base membership.  `tenko-base` requires exactly this set plus
  `package_specs/tenko-base/requires-extra`.
- `aliases` — base name → spec directory when they differ (`pcre` → `pcre2`,
  `libelf` → `elfutils`, …).
- `build_order` — the order used to rebuild the base set; it includes
  bootstrap extras and the tenko glue packages.  It is the only build-order
  manifest in the tree (see [build.md](build.md#build-order)).

Each package's `package_specs/<name>/sources` file is the only source URL and
hash data.  A version bump updates the spec and that file; nothing else pins
the version.

## Regenerating the base meta-package

After changing `base.json` or `package_specs/tenko-base/requires-extra`,
regenerate the `tenko-base` Requires block:

```sh
./tenko base-requires            # rewrite the spec in place
./tenko base-requires --check    # exit 1 if the block is stale
```
