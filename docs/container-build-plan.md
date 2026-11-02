# Container build plan — build/runtime deps, minimal rootfs, caches

Status: **proposal, not implemented.** Written 2026-11-02 on `lfs-r13.1`.
This formalizes what the ad-hoc build environment does today into four
independently useful layers, then phases them in order of risk.

Scope: how we build RPMs. Not how we install, publish or boot them.

---

## 1. Why

The build environment works but is not *described* anywhere:

- Every driver runs `rpmbuild -bb --nodeps`
  (`scripts/container_build_base.sh`, `scripts/build_x11_utils.sh`), so
  `BuildRequires` is decoration. Only 72 of 551 specs declare any.
- The build root is a hand-assembled blob. `build/rootfs-htop` (123 packages,
  781 MB, the same package set as the `localhost/browneye/build-htop:13.1`
  image) has no record of *why* a package is in it: no manifest, no
  `/etc/passwd` (sysusers was never run), no `/build`, no profile name. The X11
  wave then commits further images (`x11-deps`, `x11-progress`) on top.
- Caches are neither shared nor intentional. `container_build_base.sh` sets
  `PIP_CACHE_DIR` per package (`$OUT/build/$pkg/pip-cache`), so every package
  re-downloads. Nothing caches dnf metadata or packages.
  `~/rpmbuild/SOURCES` (148 MB) is the only real cache we have.

Concrete questions we cannot answer today:

1. What does package X need to build, and which of those are `-devel` RPMs we
   actually ship?
2. Why is package Y in the toolchain, and can it go?
3. Is a wave rebuild using the same build inputs as the previous one?

## 2. State as measured

Survey commands are in §9.

| Fact | Value |
|---|---|
| Specs | 551 (`package_specs/*/*.spec`) |
| Specs with `BuildRequires` | 72 (134 lines total) |
| Specs with explicit `Requires` | 173 |
| Subpackages by suffix | 88 `devel`, 58 `lang`, 42 `doc`, 24 `static`, 5 `libs` |
| Specs touching `AutoReq`/`AutoProv` | 21 |
| `browneye-base-build` + `browneye-build` closure | 136 packages, 279 MB download, 826 MB installed |
| `build/rootfs-htop` | 123 packages, 781 MB, no `/etc/passwd`, has `ld.so.cache` |
| Published repo | 584 RPMs, `primary` + `filelists` + `other` + `updateinfo` metadata |
| Host | Browneye 13.1 itself, uid 1000, dnf 4.24.0, rpm 4.18.1-4, createrepo_c present |

Two useful consequences:

- **The solver already exists.** RPM/dnf resolves the closure; the public repo
  metadata includes `filelists`, so file-based provides are resolvable
  offline. We do not need a custom resolver, only recorded inputs.
- **The books carry the dependency classes.** BLFS XML marks
  `Required` / `Required (at runtime)` / `Recommended` / `Optional` with
  `<xref linkend="...">` and `role="runtime"` (e.g. `x/installing/xterm.xml`),
  and `scripts/sync_blfs_spec.py` already parses book XML/entities. Intent can
  be generated rather than hand-typed.

## 3. Model

Two orthogonal axes. Keep them separate; conflating them is what produced the
fat blob.

| | **Intent** (what the spec says) | **Provenance** (what was actually used) |
|---|---|---|
| Runtime | RPM `Requires` (auto sonames + explicit) | not needed — the RPM is the artifact |
| Build | `BuildRequires` — mostly missing today | the rootfs NEVRA set at build time — never recorded today |

Rules:

- **Runtime deps stay in RPM metadata.** They are already exact and
  machine-readable from built RPMs; no new source of truth.
- **Build deps become generated data**, from books (intent) union manifests
  (provenance), with a `--check` that compares the two. A spec's
  `BuildRequires` is derived from that file for packages where we enforce it;
  it is not maintained by hand in 551 places.
- **A build is reproducible when its manifest is.** Manifest = sorted NEVRA
  list of the rootfs + repo digest + tool versions, written next to the
  output. Same manifest + same sources = same inputs.

## 4. Design

### L0 — Dependency metadata (`scripts/gen_deps.py` → `deps.lock`)

One generated JSON file at the repo root, same shape family as `lfs.lock`
(which is already the pin source). One file, not one file per package:
opencode and subagent worktrees all edit `package_specs/`, and a single
generated file keeps merge conflicts in one place.

```json
{
  "_meta": {"generator": "scripts/gen_deps.py", "book": "blfs-trunk",
            "lfs": "581459fa", "generated": "2026-11-02"},
  "packages": {
    "libxpm": {
      "build":    ["xorgproto", "libxt"],
      "runtime":  [],
      "source":   {"build": "book+manifest", "runtime": "rpm"},
      "manifest": "build/manifests/libxpm.lock"
    }
  },
  "unresolved": {"libxpm": ["libXpm"]}
}
```

- `build` / `runtime` values are canonical spec-dir names, resolved through
  `lfs.lock` aliases.
- `source` records where each field came from: `book`, `manifest`, `manual`.
- `unresolved` holds book names with no spec; `--check` fails on entries that
  stay unresolved, so gaps are visible instead of silent.
- `--check` compares `deps.lock` against (a) specs' current `BuildRequires`,
  (b) manifests of recorded builds. Exit non-zero on drift.

Generation order matters: book-derived intent first, manifests only *fill in*
what the book does not express (extra feature toggles, patches). A manifest
that disagrees with the book is a finding, not an update.

### L1 — Rootfs composer (`scripts/mkrootfs.sh`)

Replaces hand-assembled rootfs trees and committed images. Keeps the current
`rpmbuild` invocation byte-identical so "minimal" is provably the same recipe.

```
scripts/mkrootfs.sh --profile base-build                 # today's toolchain
scripts/mkrootfs.sh --deps xterm --rootfs build/rootfs-xterm
scripts/mkrootfs.sh --packages gcc make ncurses-devel --image localhost/browneye/min:13.1
```

| option | meaning |
|---|---|
| `--profile base-build` | `browneye-base-build` + `browneye-build` (the seed/fat profile) |
| `--deps PKG` | minimal closure from `deps.lock` (needs L0; P3+) |
| `--packages ...` | explicit package list, overrides profiles |
| `--rootfs DIR` / `--tarball T` / `--image REF` | outputs, any combination |
| `--manifest PATH` | default `build/manifests/<name>.lock` |
| `--engine podman-image\|podman-rootfs\|chroot` | default `podman-image` |
| `--cache DIR` | default `~/.cache/browneye` (L2) |
| `--seal` | drop the repo file and dnf config before tarball/image |

Implementation notes:

- Reuses `scripts/repo_tools.sh` (`dnf_install_packages`, `rootfs_finalize`,
  `rootfs_tarball`) so host-fallback behavior stays identical.
- `dnf … --setopt=tsflags=noscripts`, then explicit `ldconfig` and
  `systemd-sysusers` in the rootfs — this fixes the missing `/etc/passwd` that
  `rootfs-htop` has.
- Adds `/build` (workdir) and, unless `--seal`, a repo file pointing at the
  bind-mounted cache (`file:///repo`).
- **Layering:** a seed image (`rpm`, `gcc`, `binutils`, `make`,
  `glibc-devel`, `pkgconf`, `tar`, `gzip`, `xz`, `patch`, `bash`,
  `coreutils`, `findutils`, `sed`, `grep`, `gawk`) is built once; profiles and
  per-wave deps become podman image layers on top. The existing hand-committed
  `x11-deps` image becomes `--packages` over the same mechanism.
- Manifest is written *before* sealing, from `rpm -qa` inside the finished
  rootfs, with a digest of the repo directory.

Runner: `scripts/build_in_rootfs.sh` (`--rootfs`/`--image`, mounts
`package_specs:/specs:ro`, `~/rpmbuild/SOURCES:/sources:ro`, `$OUT:/out:rw`,
`--network=none`, `WORKERS=N` with a fresh instance or fresh copy per slot).
This is the P2 replacement for the container plumbing inside
`build_x11_utils.sh`; the driver keeps its build logic.

`bbuild` gets the same treatment: `builder/build.py` calls the manifest writer
after a successful build, recording the rootfs NEVRA set in a container build
and the host `rpm -qa` set for host builds. A host manifest is still useful —
it is the only record of what a one-off build ran against.

**User namespace: use the default rootless mapping, never `--userns=keep-id`.**
Container root is already mapped to the invoking host user, so writes to `/out`
land as you (measured: uid 0 inside → uid 1000 on the host; the current wave's
`xterm-412-1.x86_64.rpm` is uid 1000). `keep-id` would instead run `rpmbuild`
as uid 1000, which breaks two things: `util-linux`'s `%install` needs root
(`chown/chgrp to root/tty`, see the comment in its spec), and the payload's
`%files` ownership is taken from the buildroot, so it would record the numeric
uid instead of `root`.

This is also the real reason `rootfs_finalize` must run `systemd-sysusers` and
why the missing `/etc/passwd` in `rootfs-htop` is more than cosmetic: a spec
that names a group in `%attr` needs that name resolvable at build time. The
shipped `openssh` RPM carries `/var/lib/sshd` as `root:sshd`, so whatever
built it had the `sshd` group in its passwd/group database. Output *file*
ownership is not a problem to solve here; payload ownership is.

### L2 — Pass-through cache (`~/.cache/browneye/`)

All read-write bind mounts; none may change build output.

| cache | mount | notes |
|---|---|---|
| `repo/` | `/repo:ro`, `file:///repo` | RPMs + repodata for the 136-package closure, refreshed from the public repo by the new `scripts/sync_repo.sh --refresh` |
| `dnf/` | per-slot `--setopt=cachedir` | share `packages/` (atomic downloads, warm hits), keep metadata/solv per slot to avoid write races under `WORKERS=N` |
| `pip/` | `PIP_CACHE_DIR` | replaces the per-package cache that `container_build_base.sh` throws away |
| `cargo/`, `go/` | `CARGO_HOME`, `GOCACHE` | vendored crate / Go build caches (librsvg, tea) |
| `~/rpmbuild/SOURCES` | `/sources:ro` | unchanged; source tarball cache |

**Not included: `ccache`.** It is not in LFS or BLFS r13.1 (only mentioned as
an optional dependency of webkitgtk/swig/openjdk), so adding it needs a
user decision under `AGENTS.md`. Until then C/C++ rebuilds get no cache; the
repo/dnf cache and podman layer reuse are the portable wins.

Correctness rule for every cache: build one package cold and warm and compare
`rpm -qp` file lists and payload digests. The repo has no `SOURCE_DATE_EPOCH`
today, so byte-identical RPMs are not expected and must not be used as the
check.

### L3 — Accounting (`scripts/audit_deps.py`)

Inputs: `deps.lock`, `build/manifests/*.lock`, the repo, built RPMs. Reports:

- `undeclared` — devel/runtime packages present in a manifest that the
  package's declared set does not mention (the likely true `BuildRequires`).
- `unused` — declared but absent from the manifest.
- `missing` — declared but not resolvable in the repo.
- `stale` — manifest NEVRAs no longer in the repo.

Enforcement knob: `NO_NODEPS=1` makes the driver drop `--nodeps` for packages
whose declared set is complete. rpm then names the missing `BuildRequires`
itself, which is the real payoff of L0: `BuildRequires` starts being checked
instead of being decoration.

## 5. Phases

Each phase is usable on its own and rolls back by reverting one driver change.

| phase | deliverable | acceptance | risk |
|---|---|---|---|
| **P0** | Provenance: drivers and `bbuild` write a manifest for every build | rebuilding one package produces `build/manifests/<pkg>.lock`; the manifest reinstalls to the same NEVRA set | none — no behavior change |
| **P1** | Cache: repo mirror + dnf/pip/cargo caches + `sync_repo.sh` | cold vs warm dep install measured; identical package sets; no change to output RPM file lists | low |
| **P2** | `mkrootfs.sh` + `build_in_rootfs.sh`; `rootfs-htop` and the hand-made images retired | `--profile base-build` yields the same 136-package closure as the published meta; a wave builds through the runner | medium — touches wave drivers |
| **P3** | `gen_deps.py` + `deps.lock` from book XML and manifests; `--check` | base set has build deps for every spec that has any; `--check` passes; coverage number recorded | medium — data quality |
| **P4** | `NO_NODEPS=1` trials, leaves outward | X11 utilities wave builds strict, then base set; every failure categorized into missing-dep vs real loop | medium — build breakage isolated by package |

P0 and P1 are safe to run while opencode owns `package_specs/` (they touch
`scripts/`, `builder/` and `build/`). P3 writes only `deps.lock`, so it is also
safe. P2 changes wave drivers — coordinate. P4 must run in a worktree.

Files, per phase:

| phase | new | touched / retired |
|---|---|---|
| P0 | `builder/manifest.py` | every `rpmbuild` driver: `builder/build.py`, `scripts/build_x11_utils.sh`, `scripts/build_blfs_stack.sh`, `scripts/build_build_tools.sh`, `scripts/container_build_base.sh`, `scripts/verify_base_in_container.sh` |
| P1 | `scripts/sync_repo.sh` | `scripts/repo_tools.sh` (cache-mount helpers) |
| P2 | `scripts/mkrootfs.sh`, `scripts/build_in_rootfs.sh` | `scripts/build_x11_utils.sh` (plumbing out), `scripts/make_build_tools_image.sh` (thin alias), `scripts/chroot.sh` (retire) |
| P3 | `scripts/gen_deps.py`, `scripts/audit_deps.py`, `deps.lock` | `tests/` |
| P4 | — | `scripts/build_x11_utils.sh`, `scripts/container_build_base.sh` (`NO_NODEPS=1`) |

## 6. Non-goals

- No mock port. No `dnf builddep`-based chroot builder, no per-build package
  manager state, no `BuildRoot` conventions from Fedora.
- No hand-maintained `BuildRequires` in 551 specs. Generated data only.
- No network access during a build; sealing is the default for produced
  rootfs trees.
- No change to `browneye-base-build` as the seed profile. It stays the
  definition of "toolchain", and P3 measures how much of it is justified.
- No signing, no repo policy changes (D39 stands).
- No root requirement: `unshare -r` chroot and rootless podman only.

## 7. Risks and interactions

- **`--nodeps` is load-bearing.** 479 specs declare no build deps at all.
  Nothing in P0-P3 removes `--nodeps` globally; only P4, only per package,
  only after L0 says the declared set is complete.
- **opencode owns the X11 wave.** Its specs are being upgraded and published
  right now. The rootfs plan reads the *published* repo, so it sees the older
  X11 libs until that publish lands. Do not edit `package_specs/` for P0-P3.
- **Version parity.** Every package in the rootfs comes from the repo, which
  is already parity-audited. The only new components this plan could add are
  caches; `ccache` is not in the books and is therefore blocked on a decision
  (§8 Q5). Nothing else in P0-P2 needs a new package.
- **Host is Browneye itself.** Dependency resolution as uid 1000 through
  `unshare -r` was verified in this survey; the install path is the mechanism
  `repo_tools.sh` already uses as its host fallback, not a new privilege.
- **dnf cache concurrency.** Per-slot `cachedir` is the conservative default;
  sharing solv metadata across workers invites lock corruption for no real
  gain once `repo/` is local.
- **Manifests are only as good as the driver.** A build that bypasses
  `mkrootfs.sh`/`bbuild` produces no manifest; P0 must cover every driver we
  actually use, or the data is biased toward the new path.

## 8. Open decisions

| # | Question | Recommendation |
|---|---|---|
| Q1 | Source of truth for build deps | book XML for intent, manifests for provenance; `--check` compares them |
| Q2 | Minimality granularity | per-spec for audit (L3/P4), per-wave profiles for daily builds |
| Q3 | Default engine | `podman-image` (layer reuse), `chroot` kept for on-box/offline |
| Q4 | Cache location and concurrency | `~/.cache/browneye/`, per-slot dnf metadata, shared packages/repo |
| Q5 | `ccache` | needs an `AGENTS.md` exception decision, or explicitly drop C/C++ caching |
| Q6 | Where `deps.lock` lives and who regenerates it | repo root, `scripts/gen_deps.py`, run manually + in `--check` mode |
| Q7 | Does `browneye-base-build` remain the only fat profile | yes — it is the seed; minimality is measured against it, not instead of it |

## 9. Survey commands

```bash
# spec/dependency inventory
ls package_specs/*/*.spec | wc -l
grep -l '^BuildRequires:' package_specs/*/*.spec | wc -l
grep -h '^BuildRequires:' package_specs/*/*.spec | wc -l
grep -h '^%package ' package_specs/*/*.spec | awk '{print $NF}' | sort | uniq -c

# dependency closure of the build profile (no install, public repo)
unshare -r dnf -y --installroot /tmp/probe --releasever=13.1 \
    --repo=browneye-13.1 --setopt=install_weak_deps=False \
    --setopt=tsflags=noscripts --assumeno install browneye-base-build browneye-build

# what the ad-hoc build root actually contains
du -sh build/rootfs-htop
rpm -qa --root "$PWD/build/rootfs-htop" | wc -l
ls build/rootfs-htop/etc/passwd

# repo metadata (filelists make file-based provides resolvable offline)
curl -s https://tomfool.8bit.ca/browneye/packages/13.1/repodata/repomd.xml |
    grep -oE '<data type="[a-z]+"' | sort -u

# output ownership under rootless podman (default vs keep-id)
mkdir -p /tmp/podtest && podman run --rm --network=none \
    -v /tmp/podtest:/out:rw,z localhost/browneye/build-htop:13.1 \
    sh -c 'id; touch /out/default.txt'
ls -ln /tmp/podtest    # uid 1000, not root: container root is the host user
```

Existing pieces this plan builds on: `scripts/repo_tools.sh`,
`scripts/make_build_tools_image.sh`, `package_specs/browneye-base-build`,
`package_specs/browneye-build`, `scripts/sync_blfs_spec.py`.

Superseded when P2 lands: `scripts/make_build_tools_image.sh` (becomes a thin
alias), the ad-hoc rootfs trees, and `scripts/chroot.sh` (stale finit-era
mount script, needs root).
