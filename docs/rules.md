# Tenko packaging rules

Package-spec conventions: how to write a spec, and the rules for base
membership, `/opt` bundles, `profile.d`, `/etc/skel` and `/etc`.  Agent
workflow and publishing rules live in [`AGENTS.md`](../AGENTS.md);
build and publish commands live in [`build.md`](build.md).  Do not duplicate
those here; link.

## Writing a spec

`tests/test_spec_rules.py` (part of `./tenko check`) enforces the measurable
rules below.  Rules that older specs do not meet yet keep an allow-list in
`tests/spec_rules/`; a list may only shrink, so take a package off it when
you fix its spec.

### Layout

```
package_specs/<name>/
├── <name>.spec
├── sources       # <md5> <url> [local-filename], one line per tarball/patch download
├── nosources     # instead of sources: metapackages and packages with no download
└── files/        # patches, units, config, static filelists; linked into SOURCES
```

- `sources` URLs must be stable archive URLs: release tarballs, the LFS/BLFS
  `patches/downloads/<pkg>/` archive (never `lfs/development` or
  `blfs/svn`, which rotate).  Give the local filename as the third field when
  the URL does not end in it (`.../download`, `?raw=1`).
- Every tarball a spec unpacks needs a URL (`tests/test_sources.py`).
- Go and Rust packages download their modules or crates during `%build`
  from the upstream lockfile (`cargo build --locked`; Go checks `go.sum`)
  and declare `BuildRequires: go` or `rust` plus `make-ca` for TLS.  Keep
  the module cache inside the build tree (`GOPATH="$PWD/.gopath"`,
  `CARGO_HOME="$PWD/cargo-home"`).

### Header

```spec
Name:       socat
Version:    1.8.1.3
Release:    1
Summary:    Multipurpose relay for bidirectional data transfer
License:    GPL-2.0-only WITH openvpn-openssl-exception
URL:        http://www.dest-unreach.org/socat/
Source0:    %{name}-%{version}.tar.gz
# Why the patch is needed, in one or two lines.
Patch0:     %{name}-%{version}-openssl4.patch
Prefix:     /usr

BuildRequires: openssl
BuildRequires: readline
```

- `License` is an SPDX expression.  `Release` starts at 1 and is bumped for
  every change that alters the binary RPM.  Only the `tenko-*` glue packages
  carry `Epoch: 1`.
- `URL` is the upstream project page (the source repository when the
  project has no homepage); glue packages use
  https://github.com/pejorativefox/tenko.
- Patch files are named `<name>-<version>-<what>.patch`, live in `files/`,
  and are applied with `%patch -P N -p1` after `%setup -q`.

### Build dependencies

- Builds start from `tenko-buildroot` (the toolchain baseline in
  [build.md](build.md#metapackage-layering)).  Declare every other package
  the build uses, including headers (`openssl`, not just `openssl-libs`),
  tools (`texinfo`, `groff`, `gperf`), Python build backends
  (`python-setuptools`, `python-flit-core`) and the whole pkg-config chain a
  `.pc` file pulls in (`.pc` files generate no RPM requirements here).
- New and changed specs must build with `STRICT=1 ./tenko build <name>`.
  `./tenko builddeps --out OUT <name>` proposes missing lines from a failed
  log and the built RPMs.
- An optional dependency the package can use should be declared so the
  feature is not dropped silently; pin build-host-dependent paths (cron, unit
  and udev directories) with explicit configure options.

### Build and install

- autotools: `%configure`, `%make_build`; `%install` starts with
  `rm -rf %{buildroot}` then `%make_install`.
- meson: `meson setup .. --prefix=/usr --buildtype=release` in a `build/`
  directory, `ninja`, then `DESTDIR=%{buildroot} ninja install`.
- Remove generated junk such as `%{_infodir}/dir` in `%install`.

### Files and subpackages

- `%files -f %{_sourcedir}/<name>.filelist`: a static list in `files/`,
  generated with `./tenko filelist --rpm` or `--tree` (see
  [build.md](build.md#static-filelists)).  No globs.
- Do not own directories that `tenko-basefs` or the shared documentation
  trees own (`/usr/bin`, `/usr/share`, `/usr/share/man/man1`, ...);
  `tenko filelist` leaves them out.
- No `-devel` subpackages: headers, `.pc` files and unversioned `.so` links
  stay in the runtime package (`llvm-devel`/`clang-devel` are the only
  split).  Accepted splits are `-lang` (translations), `-doc` and `-gir`
  (introspection data), each requiring
  `%{name} = %{version}-%{release}`.

### Runtime requirements

rpm generates requirements for shared libraries, perl modules, script
interpreters and `python(abi)` (files under `/usr/lib*/pythonX.Y/`).
Declare by hand what it cannot see:

- Python module dependencies (`Requires-Dist` in the package's `.dist-info`;
  `tests/test_python_requires.py` checks them),
- tools scriptlets run: `Requires(pre): shadow` for `useradd`/`groupadd`,
- libraries opened with `dlopen()` and commands called from scripts.

### Changelog

```
* Wed Nov 11 2026 tenko <build@tenko.invalid> 1.8.1.3-1
- New package, not in the base set: latest upstream stable release
  (1.8.1.3, checked 2026-11-11).
```

State the version basis: latest upstream stable (with the date checked), a
required patch level, or a user-approved exception.  A change that only
adds `BuildRequires` does not alter the RPM and needs no Release bump; any
other rebuild of the same version needs one, because publishing refuses a
repeated NEVRA with different content.

## Base membership

- `package_specs/base.json` is the base package set: `packages` is the
  membership, `build_order` is the rebuild order.  A package there is part of
  the base system, not just a dependency of the base meta.
- `package_specs/tenko-base/requires-extra` is for requirements that are not
  base membership (distro glue, payload splits, user-requested extras).
- Changing either file is a policy change: run
  `tenko base-requires` and commit the regenerated block.

## Third-party bundles under `/opt`

`/opt` holds repackaged upstream binaries only: `nodejs`, `rust`,
`dotnet-bin`, `podman-bin`, `kitty-bin`, `firefox-bin`,
`google-chrome-bin`.  Anything Tenko compiles from source installs under
`/usr` (the source-built `go` toolchain is `/usr/lib64/go`).

- Install the versioned payload at `/opt/<name>-<version>` and keep
  `/opt/<name>` as a stable symlink.
- Link every user-facing command into `%{_bindir}` (normally `/usr/bin`).
  Paths under `/opt` are an implementation detail, not a search path.
  Desktop launchers, systemd units, cron, `sudo` and non-login shells do not
  read `/etc/profile`; a command that is only reachable through `profile.d`
  is broken in those contexts.
- Keep the payload self-contained.  Files outside `/opt` are limited to the
  command entry points, `/etc` configuration, `profile.d` snippets, licenses,
  desktop files and man pages.

## `profile.d` snippets

`/etc/profile` (from `tenko-sysconfig`) sources `/etc/profile.d/*.sh` for
login shells.  Terminal emulators start interactive non-login shells, which
read only `~/.bashrc`, so `profile.d` is not a general environment loader.

- Use `profile.d` for environment variables the application needs in a login
  shell (`GOROOT`, `DOTNET_ROOT`, ABI overrides).  A `PATH` entry is an
  optional convenience; it must never be the only way to find a command.
- POSIX `sh`, name it after the package (`dotnet.sh`), and keep
  it silent (no output, no failures from unrelated tools).
- Make it idempotent: guard `PATH` updates with
  `case ":$PATH:" in *:/opt/foo/bin:*) ;; *) PATH=... ;; esac`, because the
  same snippet can be read by more than one startup path.
- Do not source all of `/etc/profile.d` from `~/.bashrc`: several snippets
  append to `PATH` and are not idempotent.

## `/etc/skel` defaults

- Base shell startup files (`.bash_profile`, `.bashrc`) belong to
  `tenko-sysconfig`.  XFCE/desktop look and layout belong to
  `tenko-desktop-config`.  Do not scatter skel files across other packages.
- `.bash_profile` only sources `~/.bashrc`: bash reads `/etc/profile` itself
  for login shells.  `.bashrc` sources `/etc/bashrc`, the system-wide
  interactive defaults (prompt, aliases, completion, `~/.local/bin`), so it
  does not load the whole `profile.d` directory.  `/etc/profile` loads the
  same file for bash login shells, keeping one definition for both paths.
- Use `%config(noreplace)`, own the directories you create, and keep the
  files mode 0644.
- Skel only applies to accounts created after the package is installed.
  Mention the existing-account copy step in the changelog, commit message or
  issue.

## `/etc` configuration

- Mark shipped configuration `%config(noreplace)` so upgrades do not
  overwrite local edits.
- Keep runtime state out of `/etc`; use `/var/lib` or `/run`.

## Tests

Every default that can silently regress gets a `unittest` under `tests/`
(see `tests/test_base_shell.py`, `tests/test_desktop_defaults.py`,
`tests/test_no_devel_subpackages.py`, `tests/test_fdo_audit.py`).  Before
publishing run:

```sh
./tenko check
```

It runs the unit tests, `tenko base-requires --check` and the
freedesktop audit; see [`testing.md`](testing.md) for the audit modes.
