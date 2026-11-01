# Agent rules for Browneye

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
that depend on it, then record the version and the reason in `plan.md`.

## Parallel work and subagents

This tree involves long downloads, uploads, compiles, and checks. Use
subagents to run that work in parallel whenever the tasks are independent:

- Give each subagent its own git worktree and branch off the current commit.
- Keep file ownership disjoint: a subagent must not edit files the main
  session is changing.
- Let the main session own integration: review, merge, rebuild the repo,
  run boot/image tests, and publish. Subagents should not merge, publish,
  or rebuild shared images.
- Report the branch, commit, exact versions, RPM paths, and any deviations
  so the main session can merge without redoing the work.
- If a task is not independent, run it in the main session rather than
  creating a conflicting worktree.
