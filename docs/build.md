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
   when something did.  The LAN mirror is tried first, then the public site.
   `OFFLINE=1` skips the sync and uses the existing mirror.
2. **Build image** (`tenko image build`): `localhost/tenko/build:r6` is a
   root filesystem installed from the mirror (`tenko-base`,
   `tenko-base-build`, `tenko-build` and the extra build packages).  It is
   created when missing and rebuilt when the mirror has newer versions of
   its packages; `--force` rebuilds it unconditionally.
3. **Sources**: tarballs from each spec's `sources` file are fetched once and
   md5-verified into `build/sources` (a tarball already in the old
   `~/rpmbuild/SOURCES` is hard-linked instead of downloaded), then each
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

**Declared vs. undeclared build dependencies.**  Many specs do not list
their `BuildRequires` yet.  By default (`STRICT=0`) the builder installs the
declared ones that resolve and still runs `rpmbuild --nodeps` against the
image's full toolchain.  `STRICT=1` requires every `BuildRequires` to
resolve and drops `--nodeps`, so the spec must declare everything it needs.
New and updated specs should build with `STRICT=1`.

## Build image profiles

`tenko-base-build` is the build-environment meta: `tenko-base-runtime` plus
the compiler, autotools, meson/ninja/cmake and the RPM packaging macros.
Derive a build image with it instead of the runtime `tenko-base`.

It now also carries the build-only chain for Mesa's Intel CLC (`mesa_clc`):
`llvm-devel`, `llvm`, `llvm-static`, `clang-libs`, `clang-devel`,
`clang-resource-filesystem`, `spirv-headers`, `spirv-tools`,
`spirv-llvm-translator`, `python-mako` and `python-pyyaml`, plus
`vulkan-headers` for the Vulkan loader.  These provide
`llvm-config`, `LLVMSPIRVLib.pc`, `SPIRV-Tools.pc`, `libclang-cpp`,
`clang/Config/config.h`, `opencl-c.h`, the Vulkan headers and the Python
modules Mesa's build requires.

Do not recreate the old local-workaround image with zero-length LLVM `.a`
files or a stub `llvm-tblgen`.  `LLVMExports.cmake` references every installed
archive and tool binary; the build profile installs the real `llvm` and
`llvm-static` packages (the published `llvm-devel` does not pull them in) so
the CMake package check succeeds without placeholders.

The host-side counterpart is `tenko-osdev`.  It installs `tenko-base`,
`tenko-base-build`, `tenko-build`, `podman-bin`, the publish clients
(`rclone`, `rsync`, `openssh`), the ISO authoring tools and QEMU/OVMF.
Install it on a fresh Tenko system before running the build, image and
publish scripts.  `tenko-rpm-config` keeps the RPM database at the
installed-system default (`/var/lib/rpm`), so adding the development meta
to a running system does not move it.

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

Optional payload can still disappear the other way: if the build image lacks a
detected dependency, configure/meson simply does not install it and the
regenerated filelist records the smaller tree.  Bash completion is the common
case.  `tenko-base` now pulls in `bash-completion`, and packages whose build
system looks for it should require it explicitly (`BuildRequires:
bash-completion`) or set the install directory directly (`-Dbashcompdir=...`,
`-Dbash_completion=...`) so a minimal image cannot silently drop the files.
Check the rebuilt RPM with `rpm -qlp ... | grep completion` after a regen.

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
(and the `%files -f` reference).  There are no `-devel` subpackages in this
distro: headers, `.pc` files and unversioned `.so` links stay in the runtime
package.  The only intentional split is `llvm-devel`/`clang-devel`.

Regenerate filelists from a build whose dependencies were all present:
when a detected dependency (`bash-completion`, GObject introspection, ...)
is missing, the build silently installs less and the regenerated list drops
completion files or GIR typelibs.  Declaring the `BuildRequires` and building
with `STRICT=1` prevents that.

## Version bumps

Packages track the latest stable upstream release; see
[`docs/versions.md`](versions.md) and [`AGENTS.md`](../AGENTS.md).  When you
bump a package:

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
`mergerepo_c --method nvr`, uploads them, regenerates the package index, and
refreshes the LAN mirror.  It refuses a repeated NEVRA with different content,
so bump `Release` when rebuilding the same version.

```sh
PRUNE=1 ./tenko publish rpm build/wave/*.rpm   # also delete superseded RPMs
DRY_RUN=1 ./tenko publish rpm build/wave/*.rpm # stage/merge, upload nothing
MIRROR=0 ./tenko publish rpm ...               # public only (not for releases)
```

- The publish commands need `rclone`, `createrepo_c`, `mergerepo_c`, `zstd`,
  `rsync` and `ssh` (all in `tenko-osdev`, or the
  `localhost/tenko/publish-tools:r6` image).  Targets are set in
  `scripts/lib/publish.sh`.
- Everything is published twice: the public site and the LAN mirror
  (`daspork@192.168.31.9`).  Do not publish to only one.

Other publishers:

- `REPO=dir tenko publish repo` — replace the whole repository with the RPMs
  in `dir`, plus the overview page.  Use it only for a deliberate full
  republish; it deletes anything not in `dir`.
- `tenko publish iso` — installer ISO (787 MiB) + fresh `.sha256`.
- `tenko publish rootfs` — container rootfs (407 MiB) + fresh `.sha256`.

## Images

- ISO: `tenko image iso` (live root from the repo, systemd-boot ESP,
  zstd squashfs).  `ISO_AUTO=1` plus `ISO_ANSWER=tests/installer-answer.json`
  makes it unattended.
- Rootfs: `tenko image base` with
  `PACKAGES="tenko-base tenko-build python3-pyelftools"
  TARBALL=build/tenko-rootfs.tar.gz`.

The image artifacts keep the unversioned `tenko-installer.iso` and
`tenko-rootfs.tar.gz` names for now.  A future image rebuild may also publish
`tenko-installer-6.iso` and `tenko-rootfs-6.tar.gz`, with the unversioned
names kept as aliases.

Images are rebuilt only on request (see [`AGENTS.md`](../AGENTS.md)).
