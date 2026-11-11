# Agent rules for Tenko

Packaging conventions (third-party `/opt` bundles, `profile.d` snippets,
`/etc/skel` defaults, tests) live in [`docs/rules.md`](docs/rules.md).

## Tooling entry point

Build, check, image, QEMU and publish tasks all go through `./tenko`
(`./tenko help`; `./tenko COMMAND --help` for settings).  Its implementations
live in `scripts/<group>/`, with shared shell code in `scripts/lib/`.  Add new
tooling as a command in the `tenko` table rather than as a loose script, and
delete one-off helpers once their wave is done.

## Documentation

Docs describe the system as it is now and how to use it; they are not a
project history.  Git commit messages hold the history (and `%changelog`
for packages, as below).

- No changelogs, dated status reports, phase or "done" tables, test-run
  logs, "what we tried" notes or issue-by-issue narratives in docs.
- No "was", "used to", "now", "previously" or "renamed from": describe the
  current state only.  A short pointer to an open issue for a known
  limitation is fine.
- When behaviour changes, rewrite the affected doc to describe the new
  state instead of appending to it.  Delete docs (and fix links to them)
  that describe tooling, plans or features that no longer exist.
- One doc per topic; link to it instead of repeating its content.

## Do work in worktrees

Do work in a git worktree, not in the main checkout. Create worktrees under
`.worktrees/` in this repository (for example `.worktrees/<task-name>`), never
in an ad-hoc location such as `/tmp`. The directory is git-ignored, so it stays
out of `git status`; remove each worktree with `git worktree remove` once its
work is merged or discarded.

## Base package set and versions

The base package set lives in
[`package_specs/base.json`](package_specs/base.json): `packages` is the base
membership, `aliases` maps spec directory names whose package name differs
(`pcre` → `pcre2`, `libelf` → `elfutils`, …), and `build_order` is the order
used to rebuild the base system.

Packages track the latest stable upstream release.  Record the version and the
basis (upstream stable, a required patch level, or a user-approved exception)
in the `%changelog`.  Source URLs and hashes live in
`package_specs/<name>/sources`; that file is the only provenance source.
There is no global version lock.

Adding or removing a base package or changing `build_order` is a policy
change: update `base.json` and run `tenko base-requires`.  Packages
outside the base set may be added normally; if upstream has no stable release
or you need a non-latest version, say why in the changelog.

After updating a spec, rebuild and republish it before building packages
that depend on it, then record the version and the reason in the commit
message (and in the Gitea issue if the change belongs to one).

## Distro release vs package versions

The distribution release is **Tenko 6 (Workstation)**; `tenko-release`
(version 6) carries the release identity.  Upstream package versions roll
independently and keep their own versions; the `tenko-*` glue packages track
the distro release and are rebased as a group.

The distro repository is `tenko-6`: `/etc/yum.repos.d/tenko-6.repo`, id
`tenko-6`, at <https://tenko.pjfox.xyz/packages/6/>.  See
[`docs/versions.md`](docs/versions.md) for the `/etc/os-release` identity.

## Issue tracking (Gitea)

Use the `tea` CLI to read, comment on and close issues on the project's
Gitea instance (login `pjfox.xyz`, <https://pjfox.xyz/git>, repo
`daspork/tenko`): `tea issues list --repo daspork/tenko`,
`tea issues 1 --repo daspork/tenko --comments`,
`tea comments add 1 --repo daspork/tenko "text"`, and
`tea issues close 1 --repo daspork/tenko`. Do not guess the tracker
URL or use the web UI when `tea` can do the work.

## Publishing also updates the LAN mirror

Every publish must reach the local-network mirror as well as the public
site.  The publish commands already do it (`MIRROR`, default
`daspork@192.168.31.9`, `MIRROR_PUBLIC=public_html/tenko`; set
`MIRROR=0` only for a deliberate local-only test):

- `tenko publish rpm` mirrors the RPM, the merged repodata and the
  package index.
- `tenko publish repo` mirrors the whole repository and the overview
  page.
- `tenko publish iso` / `tenko publish rootfs` upload the image plus a
  fresh `.sha256` to both.

The targets are defined once, in `scripts/lib/publish.sh`.

The public bucket is `r2_tenko:tenko` (served at <https://tenko.pjfox.xyz/>).
The mirror is served at <http://192.168.31.9/~daspork/tenko/>.  Never publish
to only one of the two.

## Images are rebuilt only on request

The RPM repository is the normal delivery channel.  Fixing a package and
publishing its RPM does **not** mean rebuilding the installer ISO or the
container rootfs tarball: those artifacts are expensive to build, test and
upload, so rebuild and republish them only when the user explicitly asks
for it (or a specific issue says to).

When a package fix should eventually reach the images, note it in the
relevant issue (for example the ISO/rootfs rebuild issue) instead of
rebuilding on your own.  Existing ISOs and rootfs tarballs keep the
packages they were built with until such a rebuild.

## Parallel work and subagents

This tree involves long downloads, uploads, compiles, and checks. Use
subagents to run that work in parallel whenever the tasks are independent:

- Give each subagent its own git worktree under `.worktrees/` (see
  [Do work in worktrees](#do-work-in-worktrees)) and branch off the current
  commit.
- Keep file ownership disjoint: a subagent must not edit files the main
  session is changing.
- Let the main session own integration: review, merge, rebuild the repo,
  run boot/image tests, and publish. Subagents should not merge, publish,
  or rebuild shared images.
- Report the branch, commit, exact versions, RPM paths, and any deviations
  so the main session can merge without redoing the work.
- If a task is not independent, run it in the main session rather than
  creating a conflicting worktree.
