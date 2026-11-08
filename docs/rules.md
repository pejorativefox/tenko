# Tenko packaging rules

Package-spec conventions.  Agent workflow, publishing and LAN-mirror rules
live in [`AGENTS.md`](../AGENTS.md); build and publish commands live in
[`build.md`](build.md).  Do not duplicate those here — link.

## Base membership

- `package_specs/base.json` is the base package set: `packages` is the
  membership, `build_order` is the rebuild order.  A package there is part of
  the base system, not just a dependency of the base meta.
- `package_specs/tenko-base/requires-extra` is for requirements that are not
  base membership (distro glue, payload splits, user-requested extras).
- Changing either file is a policy change: run
  `scripts/gen_base_requires.py` and commit the regenerated block.

## Third-party bundles under `/opt`

Applies to packages that repackage an upstream binary tree: `nodejs`,
`rust`, `go-bin`, `dotnet-bin`, `podman-bin`, `kitty-bin`, `firefox-bin`,
`google-chrome-bin`.

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
- POSIX `sh`, name it after the package (`go_path.sh`, `dotnet.sh`), and keep
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
  for login shells.  `.bashrc` loads targeted snippets (for example
  `bash_completion.sh`), not the whole `profile.d` directory.
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
`tests/test_no_devel_subpackages.py`).  Before publishing run:

```sh
python3 -m unittest discover -s tests
scripts/gen_base_requires.py --check
```

## Versions and changelogs

Record the version and its basis in `%changelog`: latest stable upstream, a
required patch level, or a user-approved exception.  Source URLs and hashes
live in `package_specs/<name>/sources`.  Rebuilding the same version requires
a `Release:` bump; publishing refuses a repeated NEVRA with different
content.
