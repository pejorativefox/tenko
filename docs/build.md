# Building and publishing packages

All package sources live in `package_specs/<name>/`:

```
package_specs/curl/
├── curl.spec          # the RPM spec
├── sources            # <md5> <url> [local-filename]
└── files/             # patches, unit files, static filelists;
                       # copied into ~/rpmbuild/SOURCES by the driver
```

`build_specs.sh` builds RPMs inside a container image; the host only needs
podman and `~/rpmbuild/SOURCES` for the tarballs.

## One package

```sh
IMAGE=localhost/tenko/base:r6 \
OUT=build/my-wave \
JOBS=2 MAKE_JOBS=4 \
scripts/build_specs.sh curl/curl.spec
```

- Paths are relative to `package_specs/`.
- `IMAGE` is the build environment.  `localhost/tenko/base:r6` is the
  usual one; packages with extra requirements are built in derived images (see
  `scripts/make_base_image.sh`).
- `OUT` must be a relative path.  Results are in `$OUT/build/<pkg>/RPMS/` and
  logs in `$OUT/logs/`.
- `--from-file list.txt` builds a list instead of arguments.
- Builds are incremental: a package whose status file says `ok` is skipped, so
  re-running the same `OUT` retries only failures.

`rpmbuild` runs with `--network=none`.  Put tarballs in `~/rpmbuild/SOURCES`
first (the `sources` file gives the URL and md5), or pre-populate them with
`bbuild`.  `bbuild build <name>` is a host-side convenience for one-off builds
and source staging — **it is not the release path**; release builds go through
the container scripts.

## Build image profiles

`tenko-base-build` is the build-environment meta: `tenko-base-runtime` plus
the compiler, autotools, meson/ninja/cmake and the RPM packaging macros.
Derive a build image with it instead of the runtime `tenko-base`.

It now also carries the build-only chain for Mesa's Intel CLC (`mesa_clc`):
`llvm-devel`, `llvm`, `llvm-static`, `clang-libs`,
`clang-resource-filesystem`, `spirv-headers`, `spirv-tools`,
`spirv-llvm-translator`, `python-mako` and `python-pyyaml`.  These provide
`llvm-config`, `LLVMSPIRVLib.pc`, `SPIRV-Tools.pc`, `libclang-cpp`,
`opencl-c.h` and the Python modules Mesa's build requires.

Do not recreate the old local-workaround image with zero-length LLVM `.a`
files or a stub `llvm-tblgen`.  `LLVMExports.cmake` references every installed
archive and tool binary; the build profile installs the real `llvm` and
`llvm-static` packages (the published `llvm-devel` does not pull them in) so
the CMake package check succeeds without placeholders.

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
scripts/gen_filelist.py --rpm path/to/pkg.rpm \
    --output package_specs/pkg/files/pkg.filelist

# or from a built BUILDROOT tree (single-%files specs only; --write edits
# the spec in place, otherwise the new list is printed)
scripts/regen_files.py --spec package_specs/pkg/pkg.spec \
    --buildroot build/wave/build/pkg/BUILDROOT/pkg-<ver>-<rel>.x86_64
```

Adding a subpackage means adding both the `%package` section and its filelist
(and the `%files -f` reference).  There are no `-devel` subpackages in this
distro: headers, `.pc` files and unversioned `.so` links stay in the runtime
package.  The only intentional split is `llvm-devel`/`clang-devel`.

Build one-off waves with `IMAGE=localhost/tenko/base:r6`; the older
`base:r13.1` image predates `bash-completion` and the desktop build
dependencies, so a filelist regenerated there can lose completion files and
GIR typelibs.

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

`publish_rpm.sh` merges new RPMs into the published metadata with
`mergerepo_c --method nvr`, uploads them, regenerates the package index, and
refreshes the LAN mirror.  It refuses a repeated NEVRA with different content,
so bump `Release` when rebuilding the same version.

```sh
PRUNE=1 scripts/publish_rpm.sh build/wave/*.rpm   # also delete superseded RPMs
DRY_RUN=1 scripts/publish_rpm.sh build/wave/*.rpm # stage/merge, upload nothing
MIRROR=0 scripts/publish_rpm.sh ...               # public only (not for releases)
```

- `REMOTE`/`PORT` default to `tomfool8@tomfool.8bit.ca:53211`.  The hostname is
  deliberate: `~/.ssh/config` routes it through the local proxy.  Do not
  replace it with the raw IP.
- Everything is published twice: the public site and the LAN mirror
  (`daspork@192.168.31.9`).  Do not publish to only one.

Other publishers:

- `scripts/publish_repo.sh` — whole repository + overview page.
- `scripts/publish_iso.sh` — installer ISO (787 MiB) + fresh `.sha256`.
- `scripts/publish_rootfs.sh` — container rootfs (407 MiB) + fresh `.sha256`.

## Images

- ISO: `scripts/build_iso_uefi.sh` (live root from the repo, systemd-boot ESP,
  zstd squashfs).  `ISO_AUTO=1` plus `ISO_ANSWER=tests/installer-answer.json`
  makes it unattended.
- Rootfs: `scripts/make_base_image.sh` with
  `PACKAGES="tenko-base tenko-build python3-pyelftools"
  TARBALL=build/tenko-rootfs.tar.gz`.

The image artifacts keep the unversioned `tenko-installer.iso` and
`tenko-rootfs.tar.gz` names for now.  A future image rebuild may also publish
`tenko-installer-6.iso` and `tenko-rootfs-6.tar.gz`, with the unversioned
names kept as aliases.

Images are rebuilt only on request (see [`AGENTS.md`](../AGENTS.md)).
