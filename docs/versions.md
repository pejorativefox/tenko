# Version policy and book synchronisation

Tenko tracks the LFS and BLFS r13.1 books (the `trunk` branches of
`~/repos/lfs` and `~/repos/blfs`).  The rule, including how to handle packages
that are not in the books, is in [`AGENTS.md`](../AGENTS.md) — this page only
describes the tooling.

## The rule in one line

Every package we build or install must be **at least** the current book
version, including its dependency chain.  If a package is not in LFS/BLFS,
stop and ask before choosing a version or substitute.

## `lfs.lock`

`lfs.lock` pins the LFS release used for the base set: package names, versions,
hashes, the build order and aliases for packages whose spec name differs
(`pcre` → `pcre2`, `libelf` → `elfutils`, …).  Regenerate it when the LFS
checkout moves:

```sh
scripts/gen_lfs_lock.py
```

## Syncing a spec

`sync_lfs_spec.py` reads `lfs.lock`; `sync_blfs_spec.py` reads the BLFS
entities directly.  Both are **report-only** by default:

```sh
python3 scripts/sync_blfs_spec.py                 # show work
python3 scripts/sync_blfs_spec.py --write         # apply mechanical parts

python3 scripts/sync_lfs_spec.py                  # show work
python3 scripts/sync_lfs_spec.py --write
```

With `--write` they bump `Version:`, update the `sources` line (md5 + URL),
update `Source0`, and prepend a changelog entry.  They deliberately do not
touch configure options, patches or `%files`; anything else is printed for a
manual pass.  `--convert-files` switches a literal `%files` list to the static
`%files -f` form used by the base set.

Always review the report: a version bump often needs a build-option or patch
change that the script cannot infer.

## Auditing the tree

Two complementary tools:

```sh
# every spec against the LFS/BLFS entities (needs both checkouts)
python3 scripts/spec_audit.py

# or against a published primary.xml snapshot
python3 scripts/spec_audit.py --primary primary.xml.zst

# flat RPM-name list, counts subpackages separately
python3 scripts/audit_versions.py --rpm-dir build/devel-removal/repo
```

`spec_audit.py` reports specs below/at/above the book version, unbuilt specs,
missing patches, `Summary: TODO` and sources/version mismatches.
`spec-audit.md` is the checked-in snapshot; refresh it after a wave with the
new `primary.xml.zst` hash.

## Rebuild order

When a spec changes:

1. bump `Version`/`Release` and the changelog,
2. rebuild it (`docs/build.md`),
3. publish it to both sites (`docs/build.md`; never only one),
4. rebuild and publish anything that depends on it.

Approved deviations (packages above the book, book-less packages built from
latest upstream, retired specs) are recorded in the Gitea issues, principally
#7.  Do not silently add a new one.
