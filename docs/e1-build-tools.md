# E1 — self-hosted repo/rootfs assembly toolchain

This branch adds `dnf`, `libdnf` and `createrepo_c` (plus their dependency
stack) to the self-hosted Browneye build, so that repository and rootfs
assembly no longer needs host binaries.

## Package set

`package_specs/ORDER-BUILD` lists the build order; `scripts/build_build_tools.sh`
builds it inside `localhost/browneye/base:r13.1-selfhost-*` with
`--network=none` and installs each package into a persistent container.

LFS/BLFS packages (book versions, LFS/BLFS r13.1 trunk):

| package | version | notes |
|---|---|---|
| xz | 5.8.4 | refresh of the image's 5.8.3 (AGENTS.md parity) |
| pcre2 | 10.48 | refresh of 10.47 |
| openssl | 4.0.2 | refresh of 4.0.1 |
| curl | 8.22.0 | built with `--without-libpsl` (no libpsl in the base) |
| cmake | 4.4.3 | `bootstrap --parallel=$(nproc)` |
| python3-docutils | 0.23 | supplies `rst2man` for GLib's man pages |
| glib (pass 1 + final) | 2.90.0 | two-pass build around gobject-introspection |
| gobject-introspection | 1.86.0 | needed by the final GLib build |
| libxml2 | 2.15.4 | |
| json-c | 0.19 | |
| libgpg-error | 1.61 | |
| libassuan | 3.0.2 | |
| gpgme | 2.2.0 | |
| swig | 4.5.1 | libdnf Python bindings |
| libyaml | 0.2.5 | |
| rpm | 4.18.1-2 | rebuilt with `--enable-python`; new `python3-rpm` subpackage |

Packages that are **not** in LFS/BLFS (see “Deviations”):

| package | version | why |
|---|---|---|
| zchunk | 1.5.5 | required by librepo/createrepo_c |
| libsolv | 0.7.41 | dependency solver used by libdnf |
| libcomps | 0.1.24 | comps data, C library + Python module |
| libmodulemd | 2.15.3 | module metadata used by libdnf/createrepo_c |
| librepo | 1.21.3 | repository downloader used by libdnf |
| libdnf | 0.76.0 | dnf 4 engine (dnf5 requires rpm >= 4.19) |
| dnf | 4.24.0 | package manager |
| createrepo_c | 1.2.6 | repository metadata generator |
| browneye-build | 13.1 | meta-package (dnf + createrepo_c) |

## Build

```bash
./scripts/build_build_tools.sh                  # everything
PACKAGES="dnf createrepo_c" ./scripts/build_build_tools.sh
```

Outputs:

- `build/e1/out/build/<package>/RPMS/x86_64/*.rpm`
- `build/e1/out/logs/<package>.log`
- `build/e1/out/status/<package>`

Static filelists live in `package_specs/<package>/files/<package>.filelist`.
A package whose filelist is missing or empty is built once with
`_unpackaged_files_terminate_build 0`, the list is generated from the
buildroot with `scripts/gen_filelist_tree.py`, and the package is rebuilt
strictly. `%config` flags for `/etc/dnf/*` are added by hand afterwards.

## Integration

1. Merge the specs and `ORDER-BUILD`.
2. Build the toolchain in the self-hosted image (above), collect the RPMs
   into the repository.
3. `scripts/bootstrap_selfhosted.sh` now assembles the repo and installs the
   rootfs through `scripts/repo_tools.sh`:
   - with `TOOL_IMAGE` pointing at an image that has dnf/createrepo_c, the
     work runs inside that image;
   - otherwise it falls back to the host binaries (needed for the first
     bootstrap, because the current image does not have the tools yet).
4. `scripts/make_build_tools_image.sh` builds `…:r13.1-build-<date>` from a
   rootfs containing `browneye-base` + `browneye-build`. Pass that image as
   `TOOL_IMAGE` and the next bootstrap is fully self-hosted.
5. `scripts/assemble_repo.sh` uses the same helper for `createrepo_c`.
6. `scripts/verify_build_tools.sh` checks dnf/createrepo_c, a
   `--installroot` install (`tsflags=noscripts`), a real scriptlet install,
   and the ELF Requires of the new RPMs.

`browneye-build` is deliberately not part of `browneye-base` or
`xfce-desktop`: those metas are size-audited, and dnf/createrepo_c are build
and assembly tools.

## Deviations

- dnf, libdnf, libcomps, libmodulemd, librepo, libsolv, zchunk and
  createrepo_c are not in LFS/BLFS. Versions are the current upstream
  releases that satisfy the dependency requirements of each other and of
  rpm 4.18.1.
- dnf 5 was not used: it requires rpm >= 4.19, while the base system ships
  rpm 4.18.1. dnf 4.24 is the current release of the dnf 4 branch.
- createrepo_c is built without delta-RPM (drpm) support and without its
  Python bindings; neither is needed to create repository metadata.
- librepo is built without SELinux support (no libselinux in the distro)
  and without its Python bindings (dnf does not use them).
- libmodulemd is built without GObject Introspection and Python bindings;
  libdnf only uses its C API.
- zchunk's optional libcurl download backend is disabled (librepo does the
  downloading).
- The repo is still unsigned (`gpgcheck=0`), so gpgme's signature helpers
  are not exercised at assembly time.
