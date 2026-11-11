# Building and publishing packages

All package sources live in `package_specs/<name>/`:

```
package_specs/curl/
├── curl.spec          # the RPM spec
├── sources            # <md5> <url> [local-filename]
└── files/             # patches, unit files, static filelists;
                       # linked into the package's SOURCES by tenko build
```

Everything below goes through `./tenko` at the repository root; run
`./tenko help` for the command list and `./tenko COMMAND --help` for each
command's settings.  The implementations live in `scripts/` (one directory
per command group, shared shell code in `scripts/lib/`).

Every package is built by `tenko build` in its own fresh podman container
with the network off.  The host needs only podman; everything the builds use
is downloaded once and kept under `build/`.

## One package

```sh
OUT=build/my-wave JOBS=2 MAKE_JOBS=4 ./tenko build curl
```

- Arguments are package directories (`curl`) or spec paths relative to
  `package_specs/` (`curl/curl.spec`).
- `--from-file list.txt` builds a list instead of arguments; `--base` builds
  the whole base set from `package_specs/base.json` (the self-hosting check).
- Results are in `$OUT/build/<pkg>/RPMS/` and logs in `$OUT/logs/`; the
  command exits non-zero and lists the failures if any package failed.
- Builds are incremental: a package whose status file says `ok` is skipped, so
  re-running the same `OUT` retries only failures.

## The build environment

A build runs these steps; each is a no-op when there is nothing to do:

1. **Mirror** (`tenko sync`): the published repository is mirrored into
   `build/cache/repo` (about 3 GiB).  Each RPM is downloaded once; later
   syncs fetch only `repomd.xml` when nothing changed and only new packages
   when something did.
   `OFFLINE=1` skips the sync and uses the existing mirror.
2. **Build image** (`tenko image build [--strict]`): a root filesystem
   installed from the mirror.  `localhost/tenko/build:r6` holds `tenko-base`
   (with `tenko-base-build` and `tenko-buildroot`) plus the extra build
   packages and is used by default; `localhost/tenko/buildroot:r6`
   (`--strict`) holds only `tenko-buildroot` and is used for `STRICT=1`.
   An image is created when missing and rebuilt when the mirror has newer
   versions of its packages; `--force` rebuilds it unconditionally.
3. **Sources**: tarballs from each spec's `sources` file are fetched once and
   md5-verified into `build/sources` (a tarball found in
   `TENKO_SOURCES_SEED`, default `~/rpmbuild/SOURCES`, is hard-linked
   instead of downloaded), then each
   package gets its own `SOURCES/` with links to just its tarballs and
   `files/`.  `tenko fetch <spec-or-package>` fills the cache without
   building.
4. **Build**: a fresh container per package installs the spec's
   `BuildRequires` from `build/repo` and the mirror, then runs `rpmbuild`.
   Successful RPMs are added to `build/repo`, so a later build can use a
   package before it is published (dnf takes the highest version from the two
   repositories).  For a chain inside one run, list the packages in order and
   use `JOBS=1`.

The mirror and the source cache live in the main checkout's `build/` and are
shared by every worktree; `build/repo` is per checkout.  Delete
`build/repo` to drop local builds.

**Declared vs. undeclared build dependencies.**  Not every spec declares
all of its `BuildRequires` yet.  By default (`STRICT=0`) the
builder uses the full build image, installs the declared ones that resolve
and runs `rpmbuild --nodeps`.  `STRICT=1` builds in the `tenko-buildroot`
image, requires every `BuildRequires` to resolve and drops `--nodeps`, so the
spec must declare everything it needs.  New and updated specs should build
with `STRICT=1`.

`./tenko builddeps PKG` suggests the missing lines.  It maps the package's
built RPMs (linked libraries, `pkgconfig(...)`, `perl(...)`) and, with
`--out OUT`, the failed build log (pkg-config, meson, CMake, missing
commands and Perl modules) to providers in the mirror, and leaves out what
the buildroot or the spec already covers:

```sh
STRICT=1 OUT=build/x ./tenko build xsetroot
./tenko builddeps --out build/x xsetroot
```

## Metapackage layering

```
tenko-basefs          filesystem layout
tenko-base-runtime    the installed system (what the installer and live media use)
tenko-buildroot       toolchain baseline: core utilities, rpm + tenko-rpm-config,
                      gcc, binutils, make, patch, pkgconf, autotools, libtool,
                      bison, flex, gettext, meson/ninja/cmake, kernel headers,
                      python, glibc-locales, dnf, createrepo_c
tenko-base-build      tenko-base-runtime + tenko-buildroot + development extras
                      (gcc-lto, gperf, texinfo, tcl/expect/dejagnu, glibc-i18n,
                      Python build backends, man pages)
tenko-base            tenko-base-runtime + tenko-base-build + the base package
                      set (package_specs/base.json + requires-extra)
tenko-osdev           tenko-base + podman, publish clients, ISO tools, QEMU/OVMF
tenko-workstation     tenko-base + Node.js, podman, SSH, git, agent tools
```

`tenko-buildroot` is what package builds start from: `STRICT=1` builds run
in an image holding only it, plus the BuildRequires the spec declares.
Package-specific inputs are BuildRequires, not metapackage contents.  For
example, Mesa's Intel CLC (`mesa_clc`) needs `llvm-devel`, `llvm`,
`llvm-static`, `clang-libs`, `clang-devel`, `clang-resource-filesystem`,
`spirv-tools`, `spirv-llvm-translator`, `python-mako` and `python-pyyaml`,
and `mesa.spec` declares them.  `LLVMExports.cmake` references every
installed LLVM archive and tool binary, so LLVM consumers BuildRequire the
real `llvm` and `llvm-static` packages (`llvm-devel` does not pull them in);
do not stub them out with empty files.

Install `tenko-osdev` on a fresh Tenko system before running the build, image
and publish commands; [build-host.md](build-host.md) walks through the whole
setup.  `tenko-rpm-config` keeps the RPM database at the
installed-system default (`/var/lib/rpm`), so adding the development meta to
a running system does not move it.

`tenko image base` installs `tenko-basefs` in its own first transaction
(so the `/bin`, `/sbin`, `/lib` and `/lib64` usr-merge symlinks win over the
directories created by the rest of the transaction) and moves an RPM database
that `dnf --installroot` wrote to a real `/var/lib/rpm` into
`/usr/lib/sysimage/rpm`, where the image keeps it.

## Static filelists

`%files` is a generated, static list:

```spec
%files -f %{_sourcedir}/curl.filelist
```

The list lives in `files/<spec>.filelist`.  It is static so package contents
cannot silently change when upstream installs a new file; a build that installs
an unlisted file fails with "Installed (but unpackaged) file(s) found".

Optional payload can still disappear the other way: if the build lacks a
detected dependency (`bash-completion`, GObject introspection, ...),
configure/meson silently installs less and a regenerated filelist records the
smaller tree.  Declare those `BuildRequires` (or set the install directory
directly, e.g. `-Dbashcompdir=...`), build with `STRICT=1` before
regenerating, and check the result (`rpm -qlp ... | grep completion`).

Regenerate after a version bump or when adding/removing packages:

```sh
# from an existing RPM
./tenko filelist --rpm path/to/pkg.rpm \
    --output package_specs/pkg/files/pkg.filelist

# or from a built BUILDROOT tree
./tenko filelist --tree build/wave/build/pkg/BUILDROOT/pkg-<ver>-<rel>.x86_64 \
    --output package_specs/pkg/files/pkg.filelist

# or rewrite a spec's single inline %files section (prints a diff; --write
# edits the spec; --no-dirs omits %dir entries)
./tenko filelist --tree build/wave/build/pkg/BUILDROOT/... \
    --spec package_specs/pkg/pkg.spec --write
```

Adding a subpackage means adding both the `%package` section and its filelist
(and the `%files -f` reference).  Which splits are allowed, and the rest of
the spec conventions, are in [rules.md](rules.md#writing-a-spec).

## Version bumps

Packages track the latest stable upstream release (policy in
[`AGENTS.md`](../AGENTS.md)).  When you bump a package:

1. update `Version:` (and `Release:` back to 1, or bump the release for a
   rebuild),
2. update the matching line in `sources` (md5 + URL),
3. add a `%changelog` entry that states the basis (latest stable upstream,
   a required patch level, or a user-approved exception),
4. rebuild and publish before building packages that depend on it.

## Publishing

The distro repository is `tenko-6` (`/etc/yum.repos.d/tenko-6.repo`,
<https://tenko.pjfox.xyz/packages/6/>); package versions are independent
of the distro release.

`tenko publish rpm` merges new RPMs into the published metadata with
`mergerepo_c --method nvr`, uploads them and regenerates the package index.
It refuses a repeated NEVRA with different content, so bump `Release` when
rebuilding the same version.

```sh
PRUNE=1 ./tenko publish rpm build/wave/*.rpm   # also delete superseded RPMs
DRY_RUN=1 ./tenko publish rpm build/wave/*.rpm # stage/merge, upload nothing
```

- The publish commands need `rclone`, `createrepo_c`, `mergerepo_c`, `zstd`,
  `rsync` and `ssh` (all in `tenko-osdev`).  Targets are set in
  `scripts/lib/publish.sh`.

Other publishers:

- `REPO=dir tenko publish repo` — replace the whole repository with the RPMs
  in `dir`, plus the overview page.  Use it only for a deliberate full
  republish; it deletes anything not in `dir`.
- `tenko publish iso` — installer ISO + fresh `.sha256`.
- `tenko publish rootfs` — container rootfs tarball + fresh `.sha256`.

## Images

- ISO: `tenko image iso` (live root from the repo, systemd-boot ESP,
  zstd squashfs; layout in [`recovery.md`](recovery.md#how-tenko-boots)).
  `ISO_AUTO=1` plus `ISO_ANSWER=tests/installer-answer.json` makes it
  unattended.
- Rootfs: `tenko image base` writes `build/tenko-rootfs.tar.gz` (override
  with `TARBALL`), installing `tenko-base` plus `DEVEL_PACKAGES` by default.

The published names are `iso/tenko-installer.iso` and
`rootfs/tenko-rootfs.tar.gz`.

Images are rebuilt only on request (see [`AGENTS.md`](../AGENTS.md)).
