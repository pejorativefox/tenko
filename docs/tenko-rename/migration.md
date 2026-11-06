# Tenko rename — checkpoint 2 migration plan

- **Issue:** [#22](https://pjfox.xyz/git/daspork/browneye/issues/22)
- **Checkpoint:** 2 — compatibility and migration design
- **Branch/worktree:** `docs/tenko-migration` in `.worktrees/tenko-migration`
- **Base commit:** `752a82f` (`docs: record handle choices for the Tenko rename`)
- **Version:** 13.1 (unchanged)
- **Date:** 2026-11-06
- **Status:** design complete; local old → new upgrade proof passed; checkpoint 3
  has not started

This is the reviewable record for checkpoint 2. It defines the package
aliases, upgrade scriptlets, payload renames, repository transition, and the
local proof. It adds **only this document**; no spec, script, source or
package is changed by this commit. The generated prototype specs used for the
proof are scratch artifacts under
`.worktrees/rename-tenko/build/compat/proto/` and are not part of the tree.

The baseline and the old → new mapping are in
[`inventory.md`](inventory.md). Mapping IDs such as M12–M15, M25–M31, M39 and
M42 refer to that document.

## 1. Scope and gating

### 1.1 What checkpoint 2 delivers

- A package strategy for all 13 renamed packages: release bump, versioned
  `Obsoletes:`, versioned `Provides:` and no old-name primary packages.
- The exact `%post`/`%posttrans` snippets that migrate an installed Browneye
  13.1 system to Tenko 13.1.
- The exact `%files` and payload renames for the 13 specs.
- The repository-file transition and the aliases that stay during the
  compatibility window.
- A reproducible local upgrade test and its observed result.
- Known limits and the items checkpoint 3 must settle before it applies the
  rename.

### 1.2 What checkpoint 2 does not do

- Checkpoint 3 applies the rename to the tree: spec directories, payload
  files, `package_specs/ORDER`, build/publish scripts, installer code, docs,
  web and tests.
- Checkpoint 4 builds the renamed RPMs and runs the full clean-install and
  upgrade tests.
- Checkpoints 5 and 6 stage and cut over the repository.
- Checkpoint 7 rebuilds images. The existing ISO and rootfs still contain
  `browneye-*` packages and are expected to upgrade through the repository.
- Checkpoints 8 and 9 rename the repository/tracker and retire the aliases.

No source changes are allowed in this doc commit. The only file in this
commit is `docs/tenko-rename/migration.md`.

### 1.3 Gate

The issue defines the checkpoint-2 gate as:

> a written migration plan exists and a local old → new upgrade succeeds.

The plan is this document. The proof is §6; the passing run is
`/tmp/opencode/compat-upgrade-rootfs2.log` (`=== PASS ===`).

## 2. Package strategy

### 2.1 The 13 packages

`Release:` is bumped by one. `Version:` is unchanged, including the
`tenko-basefs` 1.0 exception. No `Epoch:` is used. The alias block is inserted
immediately after `Release:` in each spec:

```spec
# Tenko rename compatibility (issue #22).
Obsoletes: <old-name> < <new-evr>
Provides: <old-name> = %{version}-%{release}
```

| Old package | Old EVR | New package | New EVR | Exact `Obsoletes:` line | Exact `Provides:` line |
|---|---|---|---|---|---|
| `browneye-base` | 13.1-11 | `tenko-base` | 13.1-12 | `Obsoletes: browneye-base < 13.1-12` | `Provides: browneye-base = %{version}-%{release}` |
| `browneye-base-build` | 13.1-2 | `tenko-base-build` | 13.1-3 | `Obsoletes: browneye-base-build < 13.1-3` | `Provides: browneye-base-build = %{version}-%{release}` |
| `browneye-base-runtime` | 13.1-6 | `tenko-base-runtime` | 13.1-7 | `Obsoletes: browneye-base-runtime < 13.1-7` | `Provides: browneye-base-runtime = %{version}-%{release}` |
| `browneye-basefs` | 1.0-1 | `tenko-basefs` | 1.0-2 | `Obsoletes: browneye-basefs < 1.0-2` | `Provides: browneye-basefs = %{version}-%{release}` |
| `browneye-build` | 13.1-1 | `tenko-build` | 13.1-2 | `Obsoletes: browneye-build < 13.1-2` | `Provides: browneye-build = %{version}-%{release}` |
| `browneye-desktop-config` | 13.1-1 | `tenko-desktop-config` | 13.1-2 | `Obsoletes: browneye-desktop-config < 13.1-2` | `Provides: browneye-desktop-config = %{version}-%{release}` |
| `browneye-firstboot` | 13.1-2 | `tenko-firstboot` | 13.1-3 | `Obsoletes: browneye-firstboot < 13.1-3` | `Provides: browneye-firstboot = %{version}-%{release}` |
| `browneye-installer` | 13.1-24 | `tenko-installer` | 13.1-25 | `Obsoletes: browneye-installer < 13.1-25` | `Provides: browneye-installer = %{version}-%{release}` |
| `browneye-live` | 13.1-3 | `tenko-live` | 13.1-4 | `Obsoletes: browneye-live < 13.1-4` | `Provides: browneye-live = %{version}-%{release}` |
| `browneye-release` | 13.1-3 | `tenko-release` | 13.1-4 | `Obsoletes: browneye-release < 13.1-4` | `Provides: browneye-release = %{version}-%{release}` |
| `browneye-rpm-config` | 13.1-2 | `tenko-rpm-config` | 13.1-3 | `Obsoletes: browneye-rpm-config < 13.1-3` | `Provides: browneye-rpm-config = %{version}-%{release}` |
| `browneye-sysconfig` | 13.1-3 | `tenko-sysconfig` | 13.1-4 | `Obsoletes: browneye-sysconfig < 13.1-4` | `Provides: browneye-sysconfig = %{version}-%{release}` |
| `browneye-workstation` | 13.1-3 | `tenko-workstation` | 13.1-4 | `Obsoletes: browneye-workstation < 13.1-4` | `Provides: browneye-workstation = %{version}-%{release}` |

Old EVRs are the published EVRs from
[`baseline-browneye-packages.csv`](baseline-browneye-packages.csv). The new
EVR is the old release plus one, matching the prototype specs.

### 2.2 Why versioned aliases

- `Obsoletes: old < new-evr` lets RPM replace the old package with the new
  one during `dnf upgrade`, including old scratch installs that are older than
  the published EVR. The bound stops a future, higher-EVR old package (for
  example a locally built one) from being removed by this package.
- `Provides: old = %{version}-%{release}` lets packages that still require an
  old name resolve. The aliases are a safety net, not the target dependency
  graph: checkpoint 3 must update the specs that currently require
  `browneye-*` (`xfce-desktop`, `xfce-desktop-core`, `xfce-desktop-full`,
  `podman-bin`) to `tenko-*`. Checkpoint 4 must then verify there are no
  accidental old-name runtime dependencies.
- The `Provides` is versioned. A package that requires an exact old EVR
  (`browneye-base = 13.1-11`) would not be satisfied by the new alias. The
  current tree uses unversioned requires for these names, so this is not an
  immediate problem; it is a reason to update the dependent specs.

### 2.3 The `tenko-basefs` exception

`browneye-basefs` is version `1.0`, not `13.1`. Its alias must therefore be:

```spec
Obsoletes: browneye-basefs < 1.0-2
Provides: browneye-basefs = %{version}-%{release}
```

Using `< 13.1-2` here would be wrong: the old `1.0-1` still sorts below it, but
the bound would also claim to obsolete unrelated future 1.0 releases. The
new package is `tenko-basefs-1.0-2`.

### 2.4 No old-name primary packages

The build and publish set contains only `package_specs/tenko-*` and
`tenko-*.rpm`. Old names appear only as:

- `Obsoletes:`/`Provides:` metadata,
- cleanup paths in scriptlets (old repo files, units, presets, dracut configs,
  macros, installer payload, markers, boot entries),
- historical `%changelog` entries.

The old RPMs already in the published repository stay available for the
compatibility window; they are not rebuilt or republished as current
packages. `PRUNE=1` must not be used on the whole repository until the window
closes.

## 3. Migration scriptlets

The snippets below are the exact prototype spec contents. The cleanup is
layered so that a targeted package upgrade still removes its own predecessor,
and `tenko-release` owns the global catch-all. `%posttrans` runs after all
package scriptlets and obsoletes in the transaction, which is why it can clean
up anything the individual `%post` snippets did not remove.

### 3.1 `tenko-release` `%posttrans` — global cleanup

```spec
%posttrans
# Disable the old dnf repository file; keep it as .disabled for rollback.
for f in /etc/yum.repos.d/browneye-13.1.repo \
         /etc/yum.repos.d/browneye-local.repo; do
    if [ -e "$f" ]; then
        mv -f "$f" "$f.disabled"
    fi
done

# Remove old dracut/journald configuration files.  These are
# %%config(noreplace) in the old packages and can survive the obsolete.
rm -f /etc/dracut.conf.d/10-browneye.conf
rm -f /etc/systemd/journald.conf.d/10-browneye.conf

# Remove old units, presets and dracut integration.
rm -f /usr/lib/systemd/system/browneye-firstboot-root-password.service
rm -f /usr/lib/systemd/system/browneye-installer.service
rm -f /usr/lib/systemd/system-preset/90-browneye-firstboot.preset
rm -f /usr/lib/systemd/system-preset/90-browneye-live.preset
rm -f /usr/lib/dracut/dracut.conf.d/20-browneye-live.conf
rm -f /etc/systemd/system/*.wants/browneye-*

# Remove the old RPM macro tree.
rm -f /usr/lib/rpm/macros.d/macros.browneye
rm -rf /usr/lib/rpm/browneye

# Remove old installer payload.
rm -f /usr/bin/browneye-installer
rm -rf /usr/lib/browneye-installer /usr/share/doc/browneye-installer

# Migrate the first-boot marker so the prompt is not repeated.
if [ -e /var/lib/browneye/firstboot-root-password.done ] && \
   [ ! -e /var/lib/tenko/firstboot-root-password.done ]; then
    mkdir -p /var/lib/tenko
    mv -f /var/lib/browneye/firstboot-root-password.done \
        /var/lib/tenko/firstboot-root-password.done
fi
if [ -d /var/log/browneye-install ] && [ ! -d /var/log/tenko-install ]; then
    mv /var/log/browneye-install /var/log/tenko-install
fi

# Remove old package-owned markers and empty runtime directories.
rm -rf /var/lib/browneye/repo
rm -f /usr/share/browneye/base /usr/share/browneye/base-build \
      /usr/share/browneye/base-runtime /usr/share/browneye/workstation \
      /usr/share/browneye/xfce-desktop \
      /usr/share/browneye/xfce-desktop-core \
      /usr/share/browneye/xfce-desktop-full \
      /usr/share/browneye/xfce-desktop-hardware
rmdir /usr/share/browneye /var/lib/browneye /run/browneye 2>/dev/null || true

# Only remove old boot entries once a new tenko entry exists, so an upgrade
# that does not include the kernel package cannot leave the system unbootable.
if [ -d /boot/loader/entries ] && \
   ls /boot/loader/entries/tenko-*.conf >/dev/null 2>&1; then
    rm -f /boot/loader/entries/browneye-*.conf
    if [ -f /boot/loader/loader.conf ]; then
        sed -i 's/^default browneye-/default tenko-/' \
            /boot/loader/loader.conf || true
    fi
fi
```

Notes:

- `%%config` in the comment is the spec-file escape for a literal `%`.
- The old repo files are renamed, not deleted, so rollback is
  `mv browneye-13.1.repo.disabled browneye-13.1.repo`. dnf ignores files that
  do not end in `.repo`.
- The old marker/log migration is skipped when the new path already exists.
  It does not merge two existing trees.
- `/usr/share/browneye`, `/var/lib/browneye` and `/run/browneye` are removed
  with `rmdir`, not `rm -rf`: unknown or user-created files keep the directory
  in place. The explicit marker list and `/var/lib/browneye/repo` are the only
  recursive/forced removals.
- The boot-entry block is deliberately conditional. It runs only when at least
  one `tenko-*.conf` entry exists.
- `sed` only rewrites a `default browneye-<kver>` line. A hand-written
  `default browneye.conf` is not migrated; see §7.

### 3.2 `tenko-sysconfig` `%post` — old config cleanup

```spec
%post
# Remove old %%config(noreplace) configuration files.
rm -f /etc/dracut.conf.d/10-browneye.conf
rm -f /etc/systemd/journald.conf.d/10-browneye.conf
```

The new files are `/etc/dracut.conf.d/10-tenko.conf` and
`/etc/systemd/journald.conf.d/10-tenko.conf` with the same contents as the old
files. Removing the old names is required because the old dracut file was
`%config(noreplace)` and can survive the obsoleted package.

### 3.3 `tenko-firstboot` `%post` — marker and unit migration

```spec
%post
# Migrate the old first-boot marker before removing the old package paths.
if [ -e /var/lib/browneye/firstboot-root-password.done ] && \
   [ ! -e /var/lib/tenko/firstboot-root-password.done ]; then
    mkdir -p /var/lib/tenko
    mv -f /var/lib/browneye/firstboot-root-password.done \
        /var/lib/tenko/firstboot-root-password.done
fi
rm -f /etc/systemd/system/*.wants/browneye-firstboot-root-password.service
rm -f /usr/lib/systemd/system/browneye-firstboot-root-password.service
rm -f /usr/lib/systemd/system-preset/90-browneye-firstboot.preset
if command -v systemctl >/dev/null 2>&1; then
    systemctl --root=/ enable tenko-firstboot-root-password.service \
        >/dev/null 2>&1 || true
fi
```

The marker is migrated before the old package is erased so the first boot after
the upgrade does not prompt for a root password again. The old unit, preset
and wants symlink are removed, and the new unit is enabled explicitly;
the preset is not guaranteed to be re-applied on an existing system.

### 3.4 `tenko-installer` `%post` — payload and log migration

```spec
%post
# Remove the old installer payload and unit/preset/dracut integration.
rm -f /usr/lib/systemd/system/browneye-installer.service
rm -f /usr/lib/systemd/system-preset/90-browneye-live.preset
rm -f /usr/lib/dracut/dracut.conf.d/20-browneye-live.conf
rm -f /etc/systemd/system/*.wants/browneye-installer.service
rm -f /usr/bin/browneye-installer
rm -rf /usr/lib/browneye-installer /usr/share/doc/browneye-installer
if [ -d /var/log/browneye-install ] && [ ! -d /var/log/tenko-install ]; then
    mv /var/log/browneye-install /var/log/tenko-install
fi
```

The log directory is migrated as a whole. If `/var/log/tenko-install` already
exists, the old directory is left in place rather than merged.

### 3.5 `tenko-rpm-config` `%post` — old macro tree

```spec
%post
# Remove the old RPM macro directory and macro file.
rm -f /usr/lib/rpm/macros.d/macros.browneye
rm -rf /usr/lib/rpm/browneye
```

### 3.6 Marker-only packages

`tenko-base-build`, `tenko-base-runtime` and `tenko-workstation` each own a
marker under `/usr/share/tenko` and remove the corresponding old marker in
`%post`:

```spec
%post
# Remove the old marker directory left by browneye-base-build.
rm -f /usr/share/browneye/base-build
rmdir /usr/share/browneye 2>/dev/null || true
```

```spec
%post
# Remove the old marker directory left by browneye-base-runtime.
rm -f /usr/share/browneye/base-runtime
rmdir /usr/share/browneye 2>/dev/null || true
```

```spec
%post
# Remove the old marker directory left by browneye-workstation.
rm -f /usr/share/browneye/workstation
rmdir /usr/share/browneye 2>/dev/null || true
```

`tenko-base` has no `%files` payload and no `%post` cleanup; the
`/usr/share/browneye/base` marker is removed by the `tenko-release` global
cleanup.

### 3.7 Ordering and idempotence

- `tenko-sysconfig`, `tenko-rpm-config`, `tenko-firstboot` and
  `tenko-installer` clean their own predecessor paths in `%post`.
- `tenko-release` runs its `%posttrans` last and removes anything left,
  including repo files, installer payload, markers and boot entries.
- Duplicate removals are intentional. The old package's erase script may warn
  `remove failed: No such file or directory` after a new `%post` already
  removed the file. The transaction still succeeds; this was observed in the
  proof.
- All cleanup commands are best-effort and idempotent. `rmdir`, `sed` and the
  `systemctl enable` call are guarded with `2>/dev/null || true`.

## 4. File-list and payload renames

### 4.1 Summary

Every spec directory and spec file is renamed:

```text
package_specs/browneye-X/browneye-X.spec
  -> package_specs/tenko-X/tenko-X.spec
```

| New package | Spec path | Payload / file changes | `%files` delta |
|---|---|---|---|
| `tenko-base` | `package_specs/tenko-base/tenko-base.spec` | `requires-extra` content updated; `files/devel-obsoletes.inc` unchanged; no payload marker | none (empty file list) |
| `tenko-base-build` | `package_specs/tenko-base-build/tenko-base-build.spec` | none | marker path |
| `tenko-base-runtime` | `package_specs/tenko-base-runtime/tenko-base-runtime.spec` | none | marker path |
| `tenko-basefs` | `package_specs/tenko-basefs/tenko-basefs.spec` | none | none (filesystem layout unchanged) |
| `tenko-build` | `package_specs/tenko-build/tenko-build.spec` | none | none (empty) |
| `tenko-desktop-config` | `package_specs/tenko-desktop-config/tenko-desktop-config.spec` | none (`.xinitrc` generated by the spec) | none |
| `tenko-firstboot` | `package_specs/tenko-firstboot/tenko-firstboot.spec` | 4 payload files renamed; README content updated | 5 lines |
| `tenko-installer` | `package_specs/tenko-installer/tenko-installer.spec` | 5 payload files renamed; module dir and tests updated | 7 lines |
| `tenko-live` | `package_specs/tenko-live/tenko-live.spec` | none | none (empty) |
| `tenko-release` | `package_specs/tenko-release/tenko-release.spec` | `os-release` and repo file generated by the spec; empty `sources` marker kept | repo file line |
| `tenko-rpm-config` | `package_specs/tenko-rpm-config/tenko-rpm-config.spec` | `macros.browneye` renamed; `strip_debug.sh` unchanged | 2 lines |
| `tenko-sysconfig` | `package_specs/tenko-sysconfig/tenko-sysconfig.spec` | configs generated by the spec | 2 lines |
| `tenko-workstation` | `package_specs/tenko-workstation/tenko-workstation.spec` | none | marker path |

### 4.2 Exact `%files` changes

```diff
# tenko-base-build
-/usr/share/browneye/base-build
+/usr/share/tenko/base-build

# tenko-base-runtime
-/usr/share/browneye/base-runtime
+/usr/share/tenko/base-runtime

# tenko-firstboot
-/usr/libexec/browneye-firstboot-root-password
-/usr/lib/systemd/system/browneye-firstboot-root-password.service
-/usr/lib/systemd/system-preset/90-browneye-firstboot.preset
-/usr/share/doc/browneye-firstboot/README
-%dir /var/lib/browneye
+/usr/libexec/tenko-firstboot-root-password
+/usr/lib/systemd/system/tenko-firstboot-root-password.service
+/usr/lib/systemd/system-preset/90-tenko-firstboot.preset
+/usr/share/doc/tenko-firstboot/README
+%dir /var/lib/tenko

# tenko-installer
-%dir /usr/lib/browneye-installer
-/usr/lib/browneye-installer/*.py
-%{_bindir}/browneye-installer
-%{_unitdir}/browneye-installer.service
-/usr/lib/systemd/system-preset/90-browneye-live.preset
-/usr/lib/dracut/dracut.conf.d/20-browneye-live.conf
-%{_docdir}/browneye-installer/README
+%dir /usr/lib/tenko-installer
+/usr/lib/tenko-installer/*.py
+%{_bindir}/tenko-installer
+%{_unitdir}/tenko-installer.service
+/usr/lib/systemd/system-preset/90-tenko-live.preset
+/usr/lib/dracut/dracut.conf.d/20-tenko-live.conf
+%{_docdir}/tenko-installer/README

# tenko-release
-%config(noreplace) /etc/yum.repos.d/browneye-13.1.repo
+%config(noreplace) /etc/yum.repos.d/tenko-13.1.repo

# tenko-rpm-config
-%{_rpmmacrodir}/macros.browneye
-/usr/lib/rpm/browneye/strip_debug.sh
+%{_rpmmacrodir}/macros.tenko
+/usr/lib/rpm/tenko/strip_debug.sh

# tenko-sysconfig
-/etc/systemd/journald.conf.d/10-browneye.conf
+/etc/systemd/journald.conf.d/10-tenko.conf
-%config(noreplace) /etc/dracut.conf.d/10-browneye.conf
+%config(noreplace) /etc/dracut.conf.d/10-tenko.conf

# tenko-workstation
-/usr/share/browneye/workstation
+/usr/share/tenko/workstation
```

`tenko-base`, `tenko-basefs`, `tenko-build`, `tenko-desktop-config` and
`tenko-live` have no `%files` changes.

### 4.3 Payload renames

| Old path | New path |
|---|---|
| `package_specs/browneye-firstboot/files/90-browneye-firstboot.preset` | `package_specs/tenko-firstboot/files/90-tenko-firstboot.preset` |
| `package_specs/browneye-firstboot/files/browneye-firstboot-root-password` | `package_specs/tenko-firstboot/files/tenko-firstboot-root-password` |
| `package_specs/browneye-firstboot/files/browneye-firstboot-root-password.service` | `package_specs/tenko-firstboot/files/tenko-firstboot-root-password.service` |
| `package_specs/browneye-firstboot/files/README` | `package_specs/tenko-firstboot/files/README` (content rename only) |
| `package_specs/browneye-installer/files/20-browneye-live.conf` | `package_specs/tenko-installer/files/20-tenko-live.conf` |
| `package_specs/browneye-installer/files/90-browneye-live.preset` | `package_specs/tenko-installer/files/90-tenko-live.preset` |
| `package_specs/browneye-installer/files/README.browneye-installer` | `package_specs/tenko-installer/files/README.tenko-installer` |
| `package_specs/browneye-installer/files/browneye-installer` | `package_specs/tenko-installer/files/tenko-installer` |
| `package_specs/browneye-installer/files/browneye-installer.service` | `package_specs/tenko-installer/files/tenko-installer.service` |
| `package_specs/browneye-installer/files/*.py` | `package_specs/tenko-installer/files/*.py` (names unchanged; module dir becomes `/usr/lib/tenko-installer`) |
| `package_specs/browneye-installer/tests/` | `package_specs/tenko-installer/tests/` (file names unchanged; hostnames, repo ids, User-Agent and paths renamed) |
| `package_specs/browneye-rpm-config/files/macros.browneye` | `package_specs/tenko-rpm-config/files/macros.tenko` |
| `package_specs/browneye-rpm-config/files/strip_debug.sh` | `package_specs/tenko-rpm-config/files/strip_debug.sh` (name unchanged) |
| `package_specs/browneye-base/requires-extra` | `package_specs/tenko-base/requires-extra` (content rename only) |
| `package_specs/browneye-base/files/devel-obsoletes.inc` | `package_specs/tenko-base/files/devel-obsoletes.inc` (content unchanged) |

The empty `sources`/`nosources` marker files stay in the renamed spec
directories. `browneye-release/sources` is empty; it remains an empty
`tenko-release/sources`.

Content-only changes that do not rename the file:

- `tenko-firstboot/files/README`: `/var/lib/browneye` →
  `/var/lib/tenko`, unit and package names renamed.
- `tenko-installer/files/*.py`: module directory, runtime paths, labels,
  boot-entry names, log names, default hostname, repo URL and User-Agent.
- `tenko-installer/tests/*`: expected paths, hostnames, repo ids and fixture
  strings.
- `tenko-rpm-config/files/strip_debug.sh`: no old name in the script; it is
  installed under `/usr/lib/rpm/tenko/`.
- `tenko-base/requires-extra`: `browneye-rpm-config`, `browneye-basefs`,
  `browneye-sysconfig`, `browneye-release`, `browneye-firstboot` →
  `tenko-*`.
- `tenko-base/files/devel-obsoletes.inc`: unchanged; it only lists
  `-devel` packages.

## 5. Repository transition

### 5.1 New repo file

`tenko-release` generates `/etc/yum.repos.d/tenko-13.1.repo`:

```ini
[tenko-13.1]
name=Tenko Linux 13.1
baseurl=https://repo.pjfox.xyz/tenko/packages/13.1/
enabled=1
gpgcheck=0
repo_gpgcheck=0
skip_if_unavailable=1
```

It is installed as `%config(noreplace)`, so local edits are preserved on later
upgrades. The repo id changes from `browneye-13.1` to `tenko-13.1`. The
installer writes the same `tenko-13.1` id on the target, so the installed repo
file replaces the shipped one rather than duplicating it.

The baseurl is the canonical Tenko path. Until checkpoint 6 cuts production
over, the local proof does **not** fetch it; the test uses
`--repofrompath` against local directories. Checkpoints 5 and 6 make the URL
resolve and keep the old path serving the compatibility repo.

### 5.2 Old repo files

| Old file | Action | Result |
|---|---|---|
| `/etc/yum.repos.d/browneye-13.1.repo` | `%posttrans` renames it if it still exists | `browneye-13.1.repo.disabled` |
| `/etc/yum.repos.d/browneye-local.repo` | `%posttrans` renames it if it still exists | `browneye-local.repo.disabled` |

Two outcomes are acceptable for `browneye-13.1.repo`:

- RPM removes the unmodified `%config(noreplace)` file when the old package is
  obsoleted. The passing proof saw this outcome: only `tenko-13.1.repo`
  remained.
- The file was modified locally and survives the erase. The `%posttrans`
  renames it to `.disabled`.

`.disabled` is inert because dnf only reads `*.repo`. Keeping it allows a
rollback by renaming it back. Do not delete the old file in the migration; the
rename is reversible.

### 5.3 Compatibility aliases kept during the window

| Alias | Old value | New value | Action during the window |
|---|---|---|---|
| R2 bucket | `r2:browneye` | unchanged | Keep the bucket; only keys move under `tenko/`. |
| R2 key prefix | `r2:browneye/packages/13.1/` | `r2:browneye/tenko/packages/13.1/` | Keep the old key as an alias. |
| Public repo URL | `https://repo.pjfox.xyz/packages/13.1/` | `https://repo.pjfox.xyz/tenko/packages/13.1/` | Old URL keeps serving the compatibility repo. |
| LAN mirror path | `public_html/browneye` | `public_html/tenko` | Move to the new path; leave `browneye` as a symlink. |
| LAN URL | `http://192.168.31.9/~daspork/browneye/` | `http://192.168.31.9/~daspork/tenko/` | Old URL resolves through the symlink. |
| Installer ISO | `browneye-installer.iso` | `tenko-installer.iso` | Keep the old artifact; new name only after a rebuild. |
| Container rootfs | `browneye-rootfs.tar.gz` | `tenko-rootfs.tar.gz` | Keep the old artifact; new name only after a rebuild. |
| Container image | `localhost/browneye/base:r13.1` | `localhost/tenko/base:r13.1` | Keep the old tag until checkpoint 7; scripts prefer the new tag and fall back. |

The old RPMs in the repository are not pruned. `PRUNE=1` on the whole
repository would remove superseded packages the compatibility story wants to
keep.

### 5.4 Publishing order

This checkpoint does not publish anything. The order is:

1. Checkpoint 3 applies the rename to the tree.
2. Checkpoint 4 builds the RPMs and repeats the upgrade test with the full
   package set.
3. Checkpoint 5 publishes to the staging prefix and exercises a clean client.
4. Checkpoint 6 cuts production over and confirms the old aliases resolve.

Do not publish to the new R2 key or LAN path before checkpoint 5/6.

## 6. Upgrade test recipe and result

### 6.1 Environment and artifacts

The proof used a container with:

- `/published` — a copy of the published 13.1 repository;
- `/repo` — the local staging repository built from the 13 prototype specs;
- `/out/old-root` — a scratch `dnf --installroot` rootfs pre-populated with
  the old packages.

The scratch rootfs was created with `dnf --installroot` before the recorded
run. The recorded run starts at the seed block below; the pre-seeded rootfs
contained `browneye-base-13.1-9`, `browneye-basefs-1.0-1`,
`browneye-firstboot-13.1-2`, `browneye-release-13.1-2`,
`browneye-rpm-config-13.1-2` and `browneye-sysconfig-13.1-3`. These are older
than the published EVRs, but every one is below the new EVR and is covered by
the versioned `Obsoletes`.

The passing log is `/tmp/opencode/compat-upgrade-rootfs2.log`; the driver is
`/tmp/opencode/compat-upgrade-rootfs.sh`.

### 6.2 Seed the old state

```sh
ROOT=/out/old-root
mkdir -p "$ROOT/dev" "$ROOT/var/lib/browneye" \
         "$ROOT/var/log/browneye-install" "$ROOT/usr/share/browneye"
: > "$ROOT/dev/null"
: > "$ROOT/var/lib/browneye/firstboot-root-password.done"
echo old-log > "$ROOT/var/log/browneye-install/test.log"
: > "$ROOT/usr/share/browneye/xfce-desktop"
systemctl --root="$ROOT" enable browneye-firstboot-root-password.service
```

The regular `$ROOT/dev/null` is required: scriptlet redirections such as
`>/dev/null 2>&1` resolve inside the installroot, and without the file the
scriptlets print errors and the migration is less trustworthy.

### 6.3 Upgrade

```sh
dnf -y --nogpgcheck --installroot "$ROOT" --releasever=13.1 \
    --disablerepo='*' \
    --repofrompath=tenko,file:///repo \
    --repofrompath=published,file:///published \
    --setopt=install_weak_deps=False \
    upgrade --allowerasing
```

`--allowerasing` lets dnf replace the old packages through the obsoletes.
`--disablerepo='*'` makes the run depend only on the two local repositories.
`--nogpgcheck` is for the unsigned local staging repo.

### 6.4 Verify

The driver asserts, among other things:

```sh
ROOT=/out/old-root

rpm --root="$ROOT" -qa | grep -E '^(browneye|tenko)-' | sort
grep -E '^(NAME|ID|PRETTY_NAME)=' "$ROOT/etc/os-release"
ls -l "$ROOT/etc/yum.repos.d/"

# old package gone, new packages installed
! rpm --root="$ROOT" -q browneye-release
rpm --root="$ROOT" -q tenko-release tenko-sysconfig tenko-firstboot \
    tenko-rpm-config tenko-base tenko-basefs

# repo transition
test -f "$ROOT/etc/yum.repos.d/tenko-13.1.repo"
test ! -e "$ROOT/etc/yum.repos.d/browneye-13.1.repo"
grep -qx '\[tenko-13.1\]' "$ROOT/etc/yum.repos.d/tenko-13.1.repo"

# old unit/preset gone; new unit enabled
test ! -e "$ROOT/usr/lib/systemd/system/browneye-firstboot-root-password.service"
test ! -e "$ROOT/usr/lib/systemd/system-preset/90-browneye-firstboot.preset"
test ! -e "$ROOT/etc/systemd/system/multi-user.target.wants/browneye-firstboot-root-password.service"
systemctl --root="$ROOT" is-enabled tenko-firstboot-root-password.service

# old configs/macros gone; new ones present
test ! -e "$ROOT/etc/dracut.conf.d/10-browneye.conf"
test ! -e "$ROOT/etc/systemd/journald.conf.d/10-browneye.conf"
test -f "$ROOT/etc/dracut.conf.d/10-tenko.conf"
test -f "$ROOT/etc/systemd/journald.conf.d/10-tenko.conf"
test ! -e "$ROOT/usr/lib/rpm/browneye/strip_debug.sh"
test ! -e "$ROOT/usr/lib/rpm/macros.d/macros.browneye"
test -f "$ROOT/usr/lib/rpm/tenko/strip_debug.sh"
test -f "$ROOT/usr/lib/rpm/macros.d/macros.tenko"

# old markers/logs gone; new marker/log present
test ! -e "$ROOT/usr/share/browneye/xfce-desktop"
test ! -d "$ROOT/usr/share/browneye"
test -f "$ROOT/var/lib/tenko/firstboot-root-password.done"
test ! -e "$ROOT/var/lib/browneye/firstboot-root-password.done"
test ! -d "$ROOT/var/lib/browneye"
test -f "$ROOT/var/log/tenko-install/test.log"
test ! -d "$ROOT/var/log/browneye-install"
```

### 6.5 Observed result

Before:

```text
browneye-base-13.1-9.x86_64
browneye-basefs-1.0-1.x86_64
browneye-firstboot-13.1-2.x86_64
browneye-release-13.1-2.x86_64
browneye-rpm-config-13.1-2.x86_64
browneye-sysconfig-13.1-3.x86_64
NAME="Browneye Linux"
ID=browneye
PRETTY_NAME="Browneye Linux 13.1"
-rw-r--r-- 1 root root 156 ... browneye-13.1.repo
enabled
```

The transaction installed and obsoleted the packages:

```text
Installing:
 tenko-base      13.1-12  replacing browneye-base 13.1-9
 ...
 tenko-basefs    1.0-2    replacing browneye-basefs 1.0-1
 tenko-firstboot 13.1-3   replacing browneye-firstboot 13.1-2
 tenko-release   13.1-4   replacing browneye-release 13.1-2
 tenko-rpm-config 13.1-3  replacing browneye-rpm-config 13.1-2
 tenko-sysconfig 13.1-4   replacing browneye-sysconfig 13.1-3
...
Complete!
```

After:

```text
tenko-base-13.1-12.x86_64
tenko-basefs-1.0-2.x86_64
tenko-firstboot-13.1-3.x86_64
tenko-release-13.1-4.x86_64
tenko-rpm-config-13.1-3.x86_64
tenko-sysconfig-13.1-4.x86_64
NAME="Tenko Linux"
ID=tenko
PRETTY_NAME="Tenko Linux 13.1"
total 4
-rw-r--r-- 1 root root 146 ... tenko-13.1.repo
```

| Check | Result |
|---|---|
| `tenko-release` installed | yes, 13.1-4 |
| `browneye-release` gone | yes; the driver fails if `rpm -q browneye-release` succeeds |
| `/etc/os-release` | `NAME="Tenko Linux"`, `ID=tenko`, `PRETTY_NAME="Tenko Linux 13.1"` |
| Old repo file | gone; only `tenko-13.1.repo` remains (the `.disabled` branch is also accepted) |
| Old firstboot unit | file and wants symlink gone; `is-enabled` no longer succeeds (reports `not-found` once the file is removed) |
| New firstboot unit | `enabled`; unit and preset present |
| Old dracut/journald configs | `10-browneye.conf` files gone |
| New dracut/journald configs | `10-tenko.conf` files present |
| Old RPM macros | `/usr/lib/rpm/browneye/` and `macros.browneye` gone |
| New RPM macros | `/usr/lib/rpm/tenko/` and `macros.tenko` present |
| Old marker dir | `/usr/share/browneye/xfce-desktop` gone; `/usr/share/browneye` removed |
| Firstboot marker | migrated to `/var/lib/tenko/firstboot-root-password.done`; old marker gone |
| Installer log | migrated to `/var/log/tenko-install/test.log`; old dir gone |
| `tenko-build` | not installed because `browneye-build` was not in this old rootfs |

The driver exited `=== PASS ===`. Checks in the driver are silent on success,
so the log shows the section headings without per-check output; the final
`PASS` is the assertion result.

### 6.6 Caveats found during the proof

**Podman `/etc/hosts` bind mount.** The first attempt ran the upgrade inside a
podman container. It failed while unpacking `tenko-sysconfig`:

```text
error: unpacking of archive failed on file /etc/hosts;...: cpio: rename failed - Directory not empty
Error unpacking rpm package tenko-sysconfig-13.1-4.x86_64
...
Error: Transaction failed
```

The container's `/etc/hosts` is a bind mount, so RPM cannot replace it with
the package's file. The successful run used `dnf --installroot` against a
scratch directory, where `/etc/hosts` is a normal file. Do not use a
bind-mounted live `/etc` for this test.

**`/dev/null` in the scratch rootfs.** An earlier `--installroot` run lacked
`$ROOT/dev/null`; scriptlet redirections failed:

```text
/var/tmp/rpm-tmp...: line 11: /dev/null: No such file or directory
```

Creating a regular `$ROOT/dev/null` before the transaction fixed it. This is a
test-harness requirement, not a package bug.

**`/proc` warning.** The `openssh` scriptlet printed a `systemd-tmpfiles`
warning that `/proc` was not mounted. It is harmless for the upgrade proof;
the package still installed and created the `sshd` user/group.

**Expected old-file removal warnings.** The old packages' erase scriptlets
warned that `browneye-firstboot-root-password.service`,
`90-browneye-firstboot.preset`, `macros.browneye` and `10-browneye.conf` were
already gone. The new `%post`/`%posttrans` removed them first. The transaction
still completed and the verification passed.

### 6.7 Coverage limits of the proof

The passing rootfs contained 6 of the 13 old packages. The run therefore
verified the `tenko-base`, `tenko-basefs`, `tenko-firstboot`,
`tenko-release`, `tenko-rpm-config` and `tenko-sysconfig` upgrade paths (and
the release-level cleanup of the old firstboot marker, logs and
`/usr/share/browneye`). It did not exercise `tenko-base-build`,
`tenko-base-runtime`, `tenko-build`, `tenko-desktop-config`,
`tenko-installer`, `tenko-live` or `tenko-workstation`.

The first, in-container attempt did plan `tenko-build` replacing
`browneye-build`; it failed on `/etc/hosts` before verification. Checkpoint 4
must repeat the test from a rootfs containing all 13 old packages before the
packages are published.

### 6.8 Clean-install ordering: bootstrap `tenko-basefs` first

The checkpoint-4 clean-install test must install `tenko-basefs` in its own
first transaction, then install `tenko-base` and the rest of the target set:

```sh
dnf -y --nogpgcheck --installroot "$ROOT" --releasever=13.1 \
    --disablerepo='*' --repofrompath=tenko,file:///repo \
    --setopt=install_weak_deps=False install tenko-basefs

dnf -y --nogpgcheck --installroot "$ROOT" --releasever=13.1 \
    --disablerepo='*' --repofrompath=tenko,file:///repo \
    --setopt=install_weak_deps=False install tenko-base
```

A literal `dnf install tenko-base` into a completely empty installroot does
install the packages, but RPM's scriptlets fail because `/bin/sh` does not
exist until `tenko-basefs` lays down `/bin -> usr/bin` late in the transaction;
in that run the firstboot unit stays disabled. Installing `tenko-basefs`
first makes the checks pass. This matches the existing project flow
(`scripts/build_iso_uefi.sh` and `scripts/qemu_boot_login.sh` install basefs
first). It is an offline-install ordering/test concern, not a package rename
defect.

## 7. Risks and limits

### 7.1 Boot entries and NVRAM

- Old NVRAM boot entries (`Browneye Linux`, `EFI/browneye`) are **not**
  removed. They remain until a reinstall or manual cleanup with `efibootmgr`.
  The migration intentionally does not touch firmware variables.
- Old systemd-boot entries are removed only when at least one
  `tenko-*.conf` entry exists. If the transaction does not include a kernel
  package, the old entries stay, which avoids leaving the system unbootable.
- `loader.conf` is updated only in that same branch, and only for a
  `default browneye-<kver>` line. A manually written `default browneye.conf`
  is left alone. Checkpoint 3 should decide whether to broaden the `sed`
  expression; it is currently an open question, not a proven regression.
- If `loader.conf` is not writable, the `sed` failure is ignored. The old
  default can then point at a removed entry.

### 7.2 Paths and configuration

- The old `/mnt/browneye` install target is not deleted. It may be a mount
  point or contain an old target tree; deleting it automatically is unsafe.
- Old `%config(noreplace)` files are explicitly removed or renamed:
  `browneye-13.1.repo` → `.disabled`, and the old dracut/journald configs are
  removed. Local edits in those config files are not preserved; the new
  `10-tenko.conf` files carry the same default content.
- `/var/lib/browneye/repo` is removed recursively. Systems that relied on the
  old offline copy of the install media lose it. Newer installers already
  dropped that copy; the repository is the supported delivery channel.
- The old marker/log migration is skipped when the new path already exists.
  It does not merge two trees. If both `/var/lib/browneye` and
  `/var/lib/tenko` contain state, the old directory is left in place and
  `rmdir` fails silently.
- The log migration is a plain `mv`. A mount point at
  `/var/log/browneye-install`, or a permission problem, can fail the
  `tenko-installer` `%post`; the test covers the normal directory case.
- `/usr/share/browneye`, `/var/lib/browneye` and `/run/browneye` are removed
  only when empty. Unknown files keep the old directory, which is deliberate.

### 7.3 Transaction and coverage

- The repo-file and boot-entry migration lives in `tenko-release`
  `%posttrans`. A targeted upgrade that does not include `tenko-release`
  cleans only the individual package's own paths; it does not rename the old
  repo file or touch boot entries. The supported base/desktop upgrade pulls
  `tenko-release` through `tenko-base`.
- The passing proof covers 6 of 13 packages and used older EVRs than the
  published ones. Checkpoint 4 must test the full 13-package set from the
  published EVRs.
- The old `.disabled` repo branch was not exercised in the passing run
  because RPM removed the unmodified old repo file first. The code path is
  simple and reversible, but checkpoint 4 should include a modified old repo
  file in at least one case.
- The new `tenko-13.1.repo` points at the canonical public URL before
  checkpoint 6 has cut it over. The proof checks the file contents but does
  not fetch that URL. Do not treat the local proof as a production repo test.

### 7.4 History and verification

- Historical `%changelog` entries stay verbatim. There are 1,297 such lines in
  the tree, including 87 in the 13 renamed specs. The checkpoint-3 verifier
  must ignore `%changelog` sections (or use an explicit allowlist); otherwise
  a literal `grep -ri browneye` cannot pass without rewriting history.
- New changelog entries use the Tenko identity
  (`tenko <build@tenko.invalid>`). Old entries keep the old identity.
- Some old names are intentional compatibility references: `Obsoletes`,
  `Provides`, cleanup paths, the `.disabled` repo file, old unit names in
  scriptlets and old artifact/URL aliases. The verifier must allowlist them.
- The old image tag, ISO and rootfs remain in place. The tree and the images
  are intentionally inconsistent until checkpoint 7 rebuilds them.

## 8. Checkpoint 2 gate

- [x] Package strategy for all 13 packages: old → new name, old → new EVR,
  exact versioned `Obsoletes:`/`Provides:`.
- [x] `browneye-basefs` 1.0 exception recorded.
- [x] No old-name primary packages; aliases are metadata only.
- [x] Exact migration snippets for `tenko-release` `%posttrans`,
  `tenko-sysconfig`, `tenko-firstboot`, `tenko-installer`,
  `tenko-rpm-config`, `tenko-base-build`, `tenko-base-runtime` and
  `tenko-workstation`.
- [x] Exact `%files` and payload renames for all 13 specs.
- [x] Repository transition: new `tenko-13.1.repo`, old repo files renamed
  `.disabled`, compatibility aliases retained.
- [x] Local old → new upgrade proof passed (`=== PASS ===`).
- [x] Risks and limits recorded.

**Open items for checkpoint 3/4:**

1. Decide whether `loader.conf` migration should also rewrite
   `default browneye.conf` (not just `default browneye-<kver>`).
2. Update `xfce-desktop`, `xfce-desktop-core`, `xfce-desktop-full` and
   `podman-bin` to require `tenko-*`; do not rely on the `Provides` aliases.
3. Repeat the upgrade test with all 13 old packages and the published EVRs,
   including a modified old repo file to exercise the `.disabled` branch.
4. Keep the checkpoint-3 verifier `%changelog`-aware and allowlist the
   intentional compatibility references.

**Gate status:** met for checkpoint 2. The design is written and the local
old → new upgrade succeeds. Checkpoint 3 may apply it to the tree; checkpoints
4–6 must still build, test and publish, and this document does not authorize a
publish.
