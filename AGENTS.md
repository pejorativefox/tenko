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
