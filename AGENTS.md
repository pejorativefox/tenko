# Agent rules for Tenko

## Version parity with LFS/BLFS

Every package we build or install **must be at least the version in the
current LFS and BLFS books**:

- LFS: `~/repos/lfs` (branch `trunk`, the r13.1 book)
- BLFS: `~/repos/blfs` (branch `trunk`, the r13.1 book)

This applies to the package being built **and its dependency chain**. Before
starting a build (especially a new package such as Mesa), audit the package
and its dependencies against the books and update any outdated specs/RPMs
first. Never build an older version just because an old spec exists.

If a package (or a required dependency/component) is **not available in
LFS/BLFS**, stop and ask the user how to proceed. Do not choose a version or
substitute a different project on your own.

After updating a spec, rebuild and republish it before building packages
that depend on it, then record the version and the reason in the commit
message (and in the Gitea issue if the change belongs to one).

## Distro release vs package versions

The distribution release is **Tenko 6 (Workstation)**; `tenko-release-6-1`
carries the release identity.  Package versions roll independently and keep
their own upstream or book versions — do not set every package to version 6.

The distro repository is `tenko-6`: `/etc/yum.repos.d/tenko-6.repo`, id
`tenko-6`, at <https://repo.pjfox.xyz/tenko/packages/6/>.  The old
`/etc/yum.repos.d/browneye-13.1.repo` is only the compatibility cleanup
target for upgrades, not the new repo.  See
[`docs/versions.md`](docs/versions.md) for the `/etc/os-release` identity.

## Issue tracking (Gitea)

Use the `tea` CLI to read, comment on and close issues on the project's
Gitea instance (login `pjfox.xyz`, <https://pjfox.xyz/git>, repo
`daspork/browneye`): `tea issues list --repo daspork/browneye`,
`tea issues 1 --repo daspork/browneye --comments`,
`tea comments add 1 --repo daspork/browneye "text"`, and
`tea issues close 1 --repo daspork/browneye`. Do not guess the tracker
URL or use the web UI when `tea` can do the work.

## Publishing also updates the LAN mirror

Every publish must reach the local-network mirror as well as the public
site.  The publish scripts already do it (`MIRROR`, default
`daspork@192.168.31.9`, `MIRROR_PUBLIC=public_html/tenko`; set
`MIRROR=0` only for a deliberate local-only test):

- `scripts/publish_rpm.sh` mirrors the RPM, the merged repodata and the
  package index.
- `scripts/publish_repo.sh` mirrors the whole repository and the overview
  page.
- `scripts/publish_iso.sh` uploads an ISO plus a fresh `.sha256` to both.

The mirror is served at <http://192.168.31.9/~daspork/tenko/>.  During the
compatibility window the old `public_html/browneye` path is a symlink to
`public_html/tenko`, so old URLs keep working.  Never publish to only one of
the two.

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

- Give each subagent its own git worktree and branch off the current commit.
- Create worktrees under `.worktrees/` in this repository (for example
  `.worktrees/<task-name>`), never inside the main checkout and never in an
  ad-hoc location such as `/tmp`. The directory is git-ignored, so it stays
  out of `git status`; remove each worktree with `git worktree remove` when
  the subagent's work is merged or discarded.
- Keep file ownership disjoint: a subagent must not edit files the main
  session is changing.
- Let the main session own integration: review, merge, rebuild the repo,
  run boot/image tests, and publish. Subagents should not merge, publish,
  or rebuild shared images.
- Report the branch, commit, exact versions, RPM paths, and any deviations
  so the main session can merge without redoing the work.
- If a task is not independent, run it in the main session rather than
  creating a conflicting worktree.
