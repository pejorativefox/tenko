# Tenko rename — checkpoint 0/1 record

- **Issue:** [#22](https://pjfox.xyz/git/daspork/browneye/issues/22)
- **Branch/worktree:** `rename/tenko` in `.worktrees/rename-tenko`
- **Base commit:** `4c0e1b9c478d25ada40423330ab5569c3fc79cbd`
  (`docs: place agent worktrees under .worktrees`)
- **Version:** 13.1 (unchanged)
- **Date:** 2026-11-06
- **Scope:** checkpoint 0 (baseline) and checkpoint 1 (inventory and impact
  map). No source or package was changed.

**Gate status:** checkpoint 0 records the locked name, commit, published
packages/artifacts and checksums, compatibility window and handles. Checkpoint
1 records a disposition for every one of the 547 files and 1,973 matching
lines, with nothing unknown. No code changed.

This document is the reviewable record for checkpoints 0 and 1. The
machine-readable appendices are in the same directory:

| File | Contents |
|---|---|
| [`baseline-packages.csv`](baseline-packages.csv) | All 692 packages in the published repodata, with SHA-256 and size. |
| [`baseline-browneye-packages.csv`](baseline-browneye-packages.csv) | The 13 published `browneye-*` packages, LAN checksum check, and planned new EVR. |
| [`mapping.tsv`](mapping.tsv) | Old → new mapping table (M01–M48). |
| [`occurrences.tsv`](occurrences.tsv) | Every matching source line with mapping IDs and disposition (1,973 rows). |
| [`file-summary.tsv`](file-summary.tsv) | Per-file occurrence counts and mapping IDs (547 files). |

## 0. Baseline

### 0.1 Naming decisions (locked 2026-11-06)

| Item | Decision |
|---|---|
| Full name | Tenko Linux |
| Short name | Tenko |
| Package prefix | `tenko-` |
| Runtime paths | `/usr/share/tenko`, `/run/tenko` |
| Repo file | `/etc/yum.repos.d/tenko-13.1.repo` |
| Artifacts | `tenko-installer.iso`, `tenko-rootfs.tar.gz` |
| Container image | `localhost/tenko/base:r13.1` (deferred until the image/rootfs is rebuilt) |
| R2 storage | Keep the `r2:browneye` bucket; use a `tenko/` key prefix |
| LAN mirror | Move to `public_html/tenko`; leave a symlink at `public_html/browneye` |
| Images | Deferred; no ISO/rootfs rebuild in this issue |
| Git repo | `daspork/tenko` |
| Version | Stays 13.1 |

### 0.2 Source baseline

- Base commit `4c0e1b9c478d25ada40423330ab5569c3fc79cbd` on `main`.
- Version 13.1, built from the LFS/BLFS r13.1 books.
- The rename branch is `rename/tenko`, created from the base commit in
  `.worktrees/rename-tenko`.
- No code changed in checkpoint 0/1; this commit only adds this record and
  its appendices.

### 0.3 Published repository baseline

The published repodata is the source of truth. Local `build/` trees are
staging/scratch and are **not** identical to the published repository.

| Item | Value |
|---|---|
| Public URL | <https://repo.pjfox.xyz/packages/13.1/> |
| R2 location | `r2:browneye/packages/13.1/` |
| Repodata revision | `1793951685` (2026-11-06T07:54:45Z) |
| `repomd.xml` SHA-256 | `b9b851c66c982b1e21b41349bfe3db3f50e2c86acb59c56880610349dccd0ff4` |
| Primary metadata | `5dff0d060e495ac77bd46e4075cde4f5ba1377c5485756e0f450c7ecc836cd0f-primary.xml.zst` |
| Primary metadata SHA-256 | `5dff0d060e495ac77bd46e4075cde4f5ba1377c5485756e0f450c7ecc836cd0f` |
| Packages in metadata | 692 distinct name/arch entries |
| `browneye-*` packages | 13 |
| Other packages | 679 |

The full 692-package list with SHA-256 checksums is
[`baseline-packages.csv`](baseline-packages.csv).

### 0.4 Published artifacts

| Artifact | Public URL | Size | SHA-256 | LAN mirror |
|---|---|---|---|---|
| Installer ISO | <https://repo.pjfox.xyz/iso/browneye-installer.iso> | 454,758,400 B (434 MiB) | `06cf19e6c76f8277af614ca8d11f7b4e5b009c0eac08834812b6cb034f4c6a66` | matches |
| Container rootfs | <https://repo.pjfox.xyz/rootfs/browneye-rootfs.tar.gz> | 256,307,011 B (244 MiB) | `870b4dcddd46457263240b89a3946bfca747e96a655fa1bbe68f13b56c233fbf` | matches |

The old artifact names stay published during the compatibility window. The
renamed artifacts will be `tenko-installer.iso` and `tenko-rootfs.tar.gz` when
the images are rebuilt (checkpoint 7).

### 0.5 Published `browneye-*` packages

Old EVR is the published EVR. New EVR is the planned EVR after the `Release:`
bump by one; the exact Obsoletes/Provides snippets are designed in
checkpoint 2.

| Old package | Old EVR | New package | New EVR |
|---|---|---|---|
| `browneye-base` | 13.1-11 | `tenko-base` | 13.1-12 |
| `browneye-base-build` | 13.1-2 | `tenko-base-build` | 13.1-3 |
| `browneye-base-runtime` | 13.1-6 | `tenko-base-runtime` | 13.1-7 |
| `browneye-basefs` | 1.0-1 | `tenko-basefs` | 1.0-2 |
| `browneye-build` | 13.1-1 | `tenko-build` | 13.1-2 |
| `browneye-desktop-config` | 13.1-1 | `tenko-desktop-config` | 13.1-2 |
| `browneye-firstboot` | 13.1-2 | `tenko-firstboot` | 13.1-3 |
| `browneye-installer` | 13.1-24 | `tenko-installer` | 13.1-25 |
| `browneye-live` | 13.1-3 | `tenko-live` | 13.1-4 |
| `browneye-release` | 13.1-3 | `tenko-release` | 13.1-4 |
| `browneye-rpm-config` | 13.1-2 | `tenko-rpm-config` | 13.1-3 |
| `browneye-sysconfig` | 13.1-3 | `tenko-sysconfig` | 13.1-4 |
| `browneye-workstation` | 13.1-3 | `tenko-workstation` | 13.1-4 |

Full checksums, sizes and the LAN-mirror comparison are in
[`baseline-browneye-packages.csv`](baseline-browneye-packages.csv).

| Package | EVR | SHA-256 | Size (B) | LAN match |
|---|---|---|---|---|
| `browneye-base` | 13.1-11 | `0b1cfd0c418a52c5d96e6af058eec518c6988e5ec622f05223e4891006868c85` | 12,509 | yes |
| `browneye-base-build` | 13.1-2 | `56948422fb548c2baabb884931a44fbf2dead98177d6e141101f8be82a9cc7ef` | 7,754 | yes |
| `browneye-base-runtime` | 13.1-6 | `7e675a2d249b9fe1ae0ed95da75c5e7ce6179fdb315b65df6f4310d0411a8052` | 9,734 | yes |
| `browneye-basefs` | 1.0-1 | `079e994c3f2f4a32deac2387fc20b58446a05ab6861da7096eb8aec9398f5cc9` | 8,541 | yes |
| `browneye-build` | 13.1-1 | `66920f065b2a59f7051f3d3ee99e8e9a118884fbcdf8b355fe1a20ffdb1ba9c3` | 6,429 | yes |
| `browneye-desktop-config` | 13.1-1 | `8efdc55d4eb6069bab4b82ade5a7ba720324f0b5f3cf3d8ed286bfb685773aa0` | 6,662 | yes |
| `browneye-firstboot` | 13.1-2 | `dace8e4419ce321b23d06821ae5ec501794cf70dee0394c21be1eb236e5828b4` | 9,363 | yes |
| `browneye-installer` | 13.1-24 | `2ff4b1409eeef0c89de559cd9c2755d667e85a5ceefbb2b055f677b195bf23fe` | 89,911 | yes |
| `browneye-live` | 13.1-3 | `1dec8c8162975dfcd3ef1f275f20a679d82a2a43099ebecfcff6c82a03ee628c` | 6,981 | yes |
| `browneye-release` | 13.1-3 | `49eccea9f861556f7d0834d33c570f336447fd81af35ca246f2ef205ab23742d` | 7,346 | yes |
| `browneye-rpm-config` | 13.1-2 | `ab38127cfb4dda97b993a67b52861aea0bf61e3dbc25ba8660bb8a867d4fb837` | 8,176 | yes |
| `browneye-sysconfig` | 13.1-3 | `a87b9d14e17b063f2a787d98b7014dac6d833d34e8cfc0de2e45de33be017436` | 10,058 | yes |
| `browneye-workstation` | 13.1-3 | `18b0550127a02bcfe89647ce896c2a1d7cdcd810c8cd88c23618b4e122f71109` | 7,328 | yes |

**Important exception:** `browneye-basefs` is version `1.0`, not `13.1`.
Its new package is `tenko-basefs-1.0-2`, and its Obsoletes must be
`browneye-basefs < 1.0-2`, not `< 13.1-2`.

### 0.6 LAN mirror baseline

The LAN mirror has every package the published metadata references, with
matching filenames and sizes. SHA-256 was verified for all 13 `browneye-*`
RPMs and both artifacts; the other 679 packages were compared by filename and
size.

| Item | Value |
|---|---|
| LAN URL | <http://192.168.31.9/~daspork/browneye/> |
| RPM files on disk | 707 |
| Packages in published metadata | 692 |
| Metadata packages missing from LAN | 0 |
| Size mismatches | 0 |
| Extra files on LAN | 15 |

The 15 extras are 14 superseded `browneye-*` RPMs plus `liblzo2-2.10-1`:

- `browneye-base-13.1-10`
- `browneye-base-runtime-13.1-3`, `-4`, `-5`
- `browneye-installer-13.1-15` through `13.1-22` (8 files)
- `browneye-live-13.1-2`
- `browneye-release-13.1-2`
- `liblzo2-2.10-1`

All 13 current `browneye-*` RPMs on the LAN mirror match the R2 metadata
SHA-256. Do not prune the extras during the compatibility window; the current
publish scripts only remove files when `PRUNE=1`, which must not be used on the
whole repository until the window closes.

### 0.7 Compatibility window

The default window is **one release cycle**: keep the `browneye-*` aliases
until Tenko 13.2 or the next repository refresh, whichever comes first. No
old-name package or compatibility path is removed in 13.1.

During the window the following stay available:

- `Obsoletes:`/`Provides:` aliases for all 13 renamed packages.
- The old `browneye-13.1.repo` file path on existing installations, cleaned up
  or disabled by the new `tenko-release` `%post`.
- The old R2 key prefix `r2:browneye/packages/13.1/` and the old public/LAN
  URLs as aliases of the new tree.
- The old LAN mirror directory `public_html/browneye` as a symlink to
  `public_html/tenko`.
- The old artifacts `browneye-installer.iso` and `browneye-rootfs.tar.gz`.
- The old container tag `localhost/browneye/base:r13.1` until checkpoint 7.
- Historical `%changelog` entries (see the finding in §1.10).

### 0.8 Domains and handles

| Item | State / action |
|---|---|
| `daspork/tenko` (Gitea) | Rename at checkpoint 8; update remotes and links then. |
| `pejorativefox/browneye` (GitHub mirror) | Rename if applicable at checkpoint 8. |
| `tenko` org/handle | Gitea/GitHub org `tenko` appears free but is not needed; the repo stays under `daspork`. GitHub user `tenko` is taken; no action. |
| LAN mirror | `public_html/tenko`, with a `public_html/browneye` symlink. |
| R2 | Keep the `r2:browneye` bucket; use `tenko/` keys. |
| `tenko.org` | Registered and parked; confirm the registrar/owner before committing to a public domain. |
| `tenko.dev`, `tenko.io`, `tenko.net` | Did not resolve in the 2026-11-06 quick check; confirm at a registrar. |
| npm `tenko` | Taken (ES2021 parser); no action for this project. |
| PyPI / crates.io `tenko` | Free; no action. |

Nothing needs to be acquired for the code rename. `repo.pjfox.xyz` remains the
artifact host for this cycle.

## 1. Inventory and impact map

### 1.1 Method

The occurrence scan is the one required by the issue:

```sh
grep -rIl --exclude-dir=.git --exclude-dir=build -i browneye .
```

In a linked worktree `.git` is a file, not a directory, so the scan also uses
`--exclude=.git` to avoid recording the worktree gitdir pointer as a hit.
Binary files, `__pycache__`, `build/`, and this new inventory directory are
excluded.

| Item | Count |
|---|---|
| Matching files | 547 |
| Matching lines | 1,973 |
| Unclassified lines | 0 |
| Lines with a planned rename | 656 |
| Historical lines kept verbatim | 1,297 |
| Lines deferred to checkpoint 8 | 16 |
| Compatibility-only lines | 4 |

The line-level table is [`occurrences.tsv`](occurrences.tsv). A line can carry
more than one mapping ID (for example a URL and a package name on the same
line); the table records all of them. The "primary disposition" counts above
use history first, then compatibility, then defer, then rename.

### 1.2 Disposition summary

| Primary disposition | Lines | Meaning |
|---|---:|---|
| `keep-history` | 1,297 | Historical `%changelog` entries and the pre-rename systemd-boot test record. Kept verbatim. |
| `rename (+alias/cleanup)` | 395 | Rename now; old path/name is cleaned up, aliased or migrated. |
| `rename` | 261 | Straight rename with no migration step. |
| `defer (checkpoint 8)` | 16 | Repository/tracker/mirror URLs; update when the Git repo is renamed. |
| `keep-compat` | 4 | `r2:browneye` bucket defaults; the bucket stays by decision. |
| **Total** | **1,973** | |

### 1.3 The 13 `browneye-*` specs

The 13 spec directories contain 38 files and 410 matching lines: 323
non-changelog lines must be renamed or migrated, and 87 are historical
changelog lines. The generated table below shows the planned package EVR and
the mapping IDs used in each directory.

| Old package | Old EVR | New package | New EVR | Lines (non-history) | Key mappings |
|---|---|---|---|---|---|
| `browneye-base` | 13.1-11 | `tenko-base` | 13.1-12 | 26 (14) | M04, M39, M43, M01, M02, M13 |
| `browneye-base-build` | 13.1-2 | `tenko-base-build` | 13.1-3 | 14 (11) | M04, M39, M43, M01, M02, M05 |
| `browneye-base-runtime` | 13.1-6 | `tenko-base-runtime` | 13.1-7 | 26 (15) | M04, M39, M43, M01, M02, M13, M05 |
| `browneye-basefs` | 1.0-1 | `tenko-basefs` | 1.0-2 | 3 (2) | M04, M39, M43, M01, M02 |
| `browneye-build` | 13.1-1 | `tenko-build` | 13.1-2 | 6 (5) | M04, M39, M43, M02 |
| `browneye-desktop-config` | 13.1-1 | `tenko-desktop-config` | 13.1-2 | 4 (3) | M04, M39, M43, M02 |
| `browneye-firstboot` | 13.1-2 | `tenko-firstboot` | 13.1-3 | 35 (33) | M04, M13, M39, M43, M01, M02, M07 |
| `browneye-installer` | 13.1-24 | `tenko-installer` | 13.1-25 | 232 (196) | M04, M39, M43, M01, M02, M11, M13, M14, M10, M30, M32, M28, M25, M06, M08, M47, M29, M03, M45, M09, M16, M15, M26, M27, M46, M34 |
| `browneye-live` | 13.1-3 | `tenko-live` | 13.1-4 | 11 (7) | M04, M39, M43, M01, M02 |
| `browneye-release` | 13.1-3 | `tenko-release` | 13.1-4 | 15 (10) | M04, M39, M43, M01, M02, M03, M15 |
| `browneye-rpm-config` | 13.1-2 | `tenko-rpm-config` | 13.1-3 | 15 (13) | M04, M39, M43, M02, M12, M03 |
| `browneye-sysconfig` | 13.1-3 | `tenko-sysconfig` | 13.1-4 | 12 (7) | M04, M39, M43, M01, M02, M14 |
| `browneye-workstation` | 13.1-3 | `tenko-workstation` | 13.1-4 | 11 (7) | M04, M39, M43, M02, M05 |

Payload-specific notes:

| Package(s) | What changes beyond the package name |
|---|---|
| `browneye-base`, `browneye-base-build`, `browneye-base-runtime`, `browneye-workstation`, `xfce-desktop*` | `/usr/share/browneye/*` marker files → `/usr/share/tenko/*` (M05). |
| `browneye-firstboot` | `browneye-firstboot-root-password.service`, `90-browneye-firstboot.preset`, `/var/lib/browneye` (M13, M07). |
| `browneye-installer` | `browneye-installer.service`, `90-browneye-live.preset`, `20-browneye-live.conf`, `/usr/lib/browneye-installer`, `/run/browneye`, `/mnt/browneye`, boot entry names, labels, kernel cmdline, log names, repo id and User-Agent (M04, M06, M09, M11, M13, M14, M15, M16, M25–M32, M34, M45–M47). |
| `browneye-release` | `NAME`, `ID=browneye`, `PRETTY_NAME`, `/etc/yum.repos.d/browneye-13.1.repo` (M01–M03, M15). |
| `browneye-rpm-config` | `/usr/lib/rpm/browneye`, `macros.browneye` (M12). |
| `browneye-sysconfig` | `/etc/systemd/journald.conf.d/10-browneye.conf`, `/etc/dracut.conf.d/10-browneye.conf` (M14). |
| `browneye-desktop-config`, `browneye-live`, `browneye-basefs`, `browneye-build` | Package name, Summary, description, Requires and `%changelog` additions only. |

### 1.4 Non-`browneye-*` specs with non-changelog references

There are 43 such spec files (including `package_specs/ORDER`). They contain
98 non-changelog lines. The rest of each file's matches are historical
changelog entries.

| Spec | Lines (non-history) | Mappings |
|---|---|---|
| `package_specs/ORDER` | 7 | M03, M04, M13 |
| `package_specs/dnf/dnf.spec` | 1 | M02 |
| `package_specs/dracut/dracut.spec` | 1 | M02 |
| `package_specs/flatpak/flatpak.spec` | 1 | M02 |
| `package_specs/font-siji/font-siji.spec` | 1 | M02 |
| `package_specs/font-terminus/font-terminus.spec` | 1 | M02 |
| `package_specs/font-ttf-unifont/font-ttf-unifont.spec` | 1 | M02 |
| `package_specs/font-ubuntu-font-family/font-ubuntu-font-family.spec` | 1 | M02 |
| `package_specs/glibc/glibc.spec` | 2 | M04 |
| `package_specs/gnutls/gnutls.spec` | 1 | M02 |
| `package_specs/google-chrome-bin/google-chrome-bin.spec` | 4 | M02, M03 |
| `package_specs/herdr/herdr.spec` | 2 | M02 |
| `package_specs/kitty-bin/kitty-bin.spec` | 1 | M02 |
| `package_specs/libburn/libburn.spec` | 1 | M02 |
| `package_specs/liberation-fonts/liberation-fonts.spec` | 1 | M03 |
| `package_specs/libisoburn/libisoburn.spec` | 2 | M02 |
| `package_specs/libisofs/libisofs.spec` | 1 | M02 |
| `package_specs/lightdm/lightdm.spec` | 1 | M02 |
| `package_specs/linux-api-headers/linux-api-headers.spec` | 1 | M02 |
| `package_specs/linux-firmware/linux-firmware.spec` | 1 | M02 |
| `package_specs/linux-pam/linux-pam.spec` | 1 | M02 |
| `package_specs/linux/linux.spec` | 8 | M01, M02, M04, M25, M45, M27, M14, M03 |
| `package_specs/make-ca/make-ca.spec` | 5 | M45, M02, M04 |
| `package_specs/mdadm/mdadm.spec` | 1 | M02 |
| `package_specs/mtools/mtools.spec` | 1 | M02 |
| `package_specs/opencode-bin/opencode-bin.spec` | 3 | M03, M02 |
| `package_specs/openssh/files/sshd_config` | 2 | M01, M02 |
| `package_specs/podman-bin/files/containers.conf` | 1 | M02 |
| `package_specs/podman-bin/files/storage.conf` | 4 | M02 |
| `package_specs/podman-bin/podman-bin.spec` | 5 | M04, M02 |
| `package_specs/pyenv/pyenv.spec` | 1 | M02 |
| `package_specs/python3-pyelftools/python3-pyelftools.spec` | 1 | M02 |
| `package_specs/qemu/qemu.spec` | 1 | M02 |
| `package_specs/squashfs-tools/squashfs-tools.spec` | 1 | M02 |
| `package_specs/sudo/files/sudoers` | 1 | M02 |
| `package_specs/sudo/sudo.spec` | 1 | M02 |
| `package_specs/systemd/systemd.spec` | 1 | M35 |
| `package_specs/tea/tea.spec` | 2 | M02 |
| `package_specs/xdg-utils/xdg-utils.spec` | 1 | M03 |
| `package_specs/xfce-desktop-core/xfce-desktop-core.spec` | 7 | M02, M04, M05 |
| `package_specs/xfce-desktop-full/xfce-desktop-full.spec` | 7 | M02, M04, M05 |
| `package_specs/xfce-desktop-hardware/xfce-desktop-hardware.spec` | 5 | M02, M05 |
| `package_specs/xfce-desktop/xfce-desktop.spec` | 6 | M02, M04, M05 |

### 1.5 Specs with only historical changelog references

| Group | Files | Lines |
|---|---:|---:|
| Non-`browneye-*` specs whose only matches are `%changelog` history | 419 | 1,090 |

These are kept verbatim. Every path is in
[`file-summary.tsv`](file-summary.tsv) and every line is in
[`occurrences.tsv`](occurrences.tsv).

### 1.6 Non-spec files

There are 47 non-spec files (scripts, docs, web, tests, build config) with 255
non-changelog lines.

| File | Lines | Mappings |
|---|---|---|
| `.gitignore` | 1 | M36 |
| `AGENTS.md` | 7 | M02,M35,M20,M21 |
| `Containerfile` | 1 | M04,M23 |
| `README.md` | 16 | M01,M02,M21,M35,M04,M22,M15,M23,M24 |
| `bbuild` | 1 | M02 |
| `docs/build.md` | 4 | M24,M04,M23 |
| `docs/installer-ux.md` | 14 | M04,M02,M03,M32 |
| `docs/systemd-boot.md` | 39 | M02,M38,M28,M01,M04,M25,M26,M27,M31,M35 |
| `docs/testing.md` | 6 | M01,M02,M04,M32,M10 |
| `docs/versions.md` | 1 | M02 |
| `iso/core.repo` | 3 | M04,M37,M03 |
| `rpmsupport/rpmmacros` | 5 | M03,M04 |
| `scripts/assemble_repo.sh` | 1 | M02 |
| `scripts/audit_versions.py` | 3 | M04 |
| `scripts/build_blfs_stack.sh` | 7 | M24,M04,M33 |
| `scripts/build_iso_uefi.sh` | 19 | M02,M04,M24,M22,M28,M33,M16,M30,M26,M25,M01,M27 |
| `scripts/build_rootfs.sh` | 3 | M04 |
| `scripts/build_specs.sh` | 3 | M02,M24 |
| `scripts/build_x11_utils.sh` | 5 | M02,M04,M24,M33 |
| `scripts/bump_to_book.py` | 1 | M48 |
| `scripts/container_build_base.sh` | 1 | M02 |
| `scripts/gen_base_requires.py` | 6 | M04 |
| `scripts/gen_lfs_lock.py` | 2 | M03 |
| `scripts/gen_repo_index.py` | 5 | M02,M01,M04,M22,M23 |
| `scripts/install.sh` | 2 | M04 |
| `scripts/make_base_image.sh` | 15 | M02,M24,M04,M16 |
| `scripts/make_initramfs.sh` | 1 | M14 |
| `scripts/prune_repo.sh` | 1 | M02 |
| `scripts/publish_iso.sh` | 4 | M04,M22,M17,M20,M21,M35 |
| `scripts/publish_repo.sh` | 14 | M02,M04,M17,M20,M01,M16,M22,M23 |
| `scripts/publish_rootfs.sh` | 5 | M04,M23,M17,M20,M21,M35 |
| `scripts/publish_rpm.sh` | 4 | M02,M17,M20,M04 |
| `scripts/qemu_boot.sh` | 4 | M02,M04,M16 |
| `scripts/qemu_boot_graphical.sh` | 2 | M04 |
| `scripts/qemu_boot_login.sh` | 11 | M04,M13,M32,M16 |
| `scripts/qemu_run_desktop.sh` | 3 | M32,M02 |
| `scripts/qemu_test_installer.sh` | 1 | M04,M22 |
| `scripts/repo_tools.sh` | 6 | M04,M24,M16 |
| `scripts/run_installer_sim.sh` | 3 | M10,M04 |
| `scripts/sync_blfs_spec.py` | 2 | M02,M48 |
| `scripts/sync_lfs_spec.py` | 1 | M48 |
| `scripts/verify_base_in_container.sh` | 5 | M02,M24,M04 |
| `spec-audit.md` | 2 | M02,M04 |
| `tests/installer-answer.json` | 1 | M04,M32 |
| `tests/test_bbuild.py` | 2 | M03 |
| `tests/test_repo_index.py` | 2 | M04,M15 |
| `web/index.html` | 30 | M01,M02,M04,M22,M15,M35,M19,M16,M23,M24 |

### 1.7 Old → new mapping table

The same table is in [`mapping.tsv`](mapping.tsv).

| ID | Old | New | Action | Notes |
|---|---|---|---|---|
| M01 | Browneye Linux | Tenko Linux | rename | Brand/full name in prose, titles and descriptions. |
| M02 | Browneye / BrownEye | Tenko | rename | Short brand name in prose, comments, summaries and docs. |
| M03 | browneye | tenko | rename | Lowercase brand/ID/hostname/prefix in prose and identifiers. |
| M04 | browneye-<pkg> | tenko-<pkg> | rename | All 13 package names; add Obsoletes/Provides aliases for the compat window. |
| M05 | /usr/share/browneye | /usr/share/tenko | rename+cleanup | Runtime data/marker directory; move/remove the old tree in %post. |
| M06 | /run/browneye | /run/tenko | rename | Runtime state/log directory; no persistent migration needed. |
| M07 | /var/lib/browneye | /var/lib/tenko | rename+cleanup | Persistent marker/state directory; migrate markers and remove old dir. |
| M08 | /var/log/browneye-install | /var/log/tenko-install | rename | Installed-system installer logs. |
| M09 | /mnt/browneye | /mnt/tenko | rename | Default installer target mount point. |
| M10 | /tmp/browneye-installer-sim, BROWNEYE_SIM_DIR | /tmp/tenko-installer-sim, TENKO_SIM_DIR | rename | Simulation scratch directory and environment variable. |
| M11 | /usr/lib/browneye-installer | /usr/lib/tenko-installer | rename | Installer Python module directory. |
| M12 | /usr/lib/rpm/browneye, macros.browneye | /usr/lib/rpm/tenko, macros.tenko | rename | RPM macro directory and macro file shipped by tenko-rpm-config. |
| M13 | browneye-* systemd units/presets | tenko-* systemd units/presets | rename+cleanup | Rename units/presets; disable/remove stale old units on upgrade. |
| M14 | 10-browneye.conf, 20-browneye-live.conf | 10-tenko.conf, 20-tenko-live.conf | rename+cleanup | Rename dracut/journald configs; remove old config files in %post. |
| M15 | browneye-13.1 repo id/file | tenko-13.1 repo id/file | rename+alias | New repo file tenko-13.1.repo; remove/disable the old browneye-13.1.repo. |
| M16 | --repofrompath=browneye | --repofrompath=tenko | rename | dnf repo id used by scripts and installer. |
| M17 | r2:browneye bucket | r2:browneye bucket | keep-compat | Bucket remains r2:browneye by decision; only the key prefix changes. |
| M18 | packages/13.1 R2 key | tenko/packages/13.1 R2 key | rename+alias | Publish under tenko/; keep packages/13.1 as a compatibility alias. |
| M19 | https://repo.pjfox.xyz/packages/13.1/ | https://repo.pjfox.xyz/tenko/packages/13.1/ | rename+alias | New public URL; old URL keeps serving the compatibility repo. |
| M20 | public_html/browneye | public_html/tenko | rename+alias | New LAN mirror root; leave a symlink at public_html/browneye. |
| M21 | http://192.168.31.9/~daspork/browneye/ | http://192.168.31.9/~daspork/tenko/ | rename+alias | New LAN URL; old URL resolves through the symlink. |
| M22 | browneye-installer.iso | tenko-installer.iso | rename+alias | New ISO artifact; keep the old ISO published during the window. |
| M23 | browneye-rootfs.tar.gz | tenko-rootfs.tar.gz | rename+alias | New rootfs artifact; keep the old tarball published during the window. |
| M24 | localhost/browneye/* images | localhost/tenko/* images | rename+compat | New image names; keep localhost/browneye/base:r13.1 until checkpoint 7. |
| M25 | browneye-<kver>.conf boot entries | tenko-<kver>.conf boot entries | rename | Kernel %post/%preun entry names and installer-written entries. |
| M26 | default browneye-* / browneye.conf | default tenko-* / tenko.conf | rename | systemd-boot loader.conf default. |
| M27 | title Browneye Linux 13.1 | title Tenko Linux 13.1 | rename | Boot menu title written by installer and kernel scriptlets. |
| M28 | BROWNEYE, BROWNEYEESP, BROWNEYE-ANSWER, browneye-swap | TENKO, TENKOESP, TENKO-ANSWER, tenko-swap | rename+compat | Filesystem/ISO labels; probe both old and new live-media labels during the window. |
| M29 | Browneye ESP/swap/Linux partition names | Tenko ESP/swap/Linux partition names | rename | GPT partition names in layout.py/disk.py. |
| M30 | browneye.auto/console/serial/dry_run/debug/answer | tenko.auto/console/serial/dry_run/debug/answer | rename+compat | Kernel command-line switches; accept old browneye.* aliases during the window. |
| M31 | --bootloader-id=browneye, EFI/browneye, Browneye Linux EFI label | --bootloader-id=tenko, EFI/tenko, Tenko Linux EFI label | rename | EFI NVRAM label/path; old entries remain until reinstall or manual cleanup. |
| M32 | browneye / browneye-test hostname, browneye1 password | tenko / tenko-test hostname, tenko1 password | rename | Installer defaults and test fixtures. |
| M33 | browneye-blfs, browneye-x11, browneye-iso-build | tenko-blfs, tenko-x11, tenko-iso-build | rename | Build/test container names. |
| M34 | Browneye-Installer/13.1 User-Agent | Tenko-Installer/13.1 User-Agent | rename | Installer HTTP User-Agent. |
| M35 | daspork/browneye, pejorativefox/browneye | daspork/tenko, pejorativefox/tenko | defer | Git repo/tracker/mirror URLs; rename and redirect at checkpoint 8. |
| M36 | browneye.iso .gitignore pattern | tenko.iso .gitignore pattern | rename+keep | Ignore the new artifact; keep the old pattern while old builds exist. |
| M37 | [browneye-core] / 192.168.31.94/browneye/repos/0.3.5-rc1 | [tenko-core] / current tenko repo | repoint | iso/core.repo is stale; rename and repoint at the current repository. |
| M38 | browneye <build@browneye.invalid> changelog history | tenko <build@tenko.invalid> for new entries | keep-history | Historical %changelog entries stay verbatim (checkpoint 9 allows history); new entries use the Tenko identity. |
| M39 | package_specs/browneye-* files | package_specs/tenko-* files | rename | Rename the 13 spec directories, spec files and their browneye-named payload files. |
| M40 | Browneye docs/web prose | Tenko docs/web prose | rename | README, AGENTS.md, docs/, web/, spec-audit.md and command examples. |
| M41 | browneye-installer-systemd.iso, browneye-installer-multidisk-test.iso | tenko-installer-systemd.iso, tenko-installer-multidisk-test.iso | rename | Historical/test build artifact names in scripts and docs. |
| M42 | browneye compatibility aliases | browneye compatibility aliases | keep-compat | Intentional old names: Obsoletes/Provides, old repo file cleanup, old units/dirs/images/artifacts/URLs. |
| M43 | 13 browneye-* spec metadata/payload | 13 tenko-* spec metadata/payload | rename | Name, Summary, description, Requires, %files, %post and %changelog additions in the 13 specs. |
| M44 | browneye test fixtures | tenko test fixtures | rename | Test hostnames, passwords, fixture strings and expected repo ids. |
| M45 | Browneye build helper/heredoc/constant names | Tenko build helper/heredoc/constant names | rename | Heredoc delimiters/temp names/constants such as BROWNEYECA, BROWNEYE_EOF, BROWNEYE_BASE_PACKAGES and .browneye-build. |
| M46 | /sys/firmware/qemu_fw_cfg/by_name/opt/browneye | /sys/firmware/qemu_fw_cfg/by_name/opt/tenko | rename | QEMU fw_cfg answer-file path used by the installer and tests. |
| M47 | browneye-install.jsonl/.log, browneye-install-failure.* | tenko-install.jsonl/.log, tenko-install-failure.* | rename | Installer log basenames copied to the ESP and /var/log. |
| M48 | browneye <build@browneye.invalid> in future changelog generators | tenko <build@tenko.invalid> | rename | Packager identity emitted by scripts/bump_to_book.py and scripts/sync_*_spec.py for new entries. |

Five rows are planned or grouping rows and have no direct line in
`occurrences.tsv`: M18 (non-literal R2 key path), M40/M44 (grouped under
M01–M03/M15/M32), M41 (test-build artifact names that currently appear only in
historical docs), and M42 (the Obsoletes/Provides and cleanup aliases to be
added in checkpoint 2). They are listed so checkpoints 2 and 3 use one mapping
vocabulary.

### 1.8 Compatibility references that must stay

| Reference | Why it stays | Where it is recorded |
|---|---|---|
| `r2:browneye` bucket | Locked decision; only keys move under `tenko/`. | M17 |
| `r2:browneye/packages/13.1/` | Compatibility alias during the window. | M18 |
| `https://repo.pjfox.xyz/packages/13.1/` and the LAN `/browneye/` URL | Old clients and old repo files still resolve. | M19, M21 |
| `public_html/browneye` | Symlink to `public_html/tenko`. | M20 |
| `browneye-installer.iso`, `browneye-rootfs.tar.gz` | Old artifacts remain published. | M22, M23 |
| `localhost/browneye/base:r13.1` | Build image not rebuilt until checkpoint 7. | M24 |
| `browneye-13.1.repo` | Old file is a `%config(noreplace)`; new `%post` must remove or disable it. | M15, M42 |
| Old `browneye-*` unit/preset/dracut files | Cleaned up on upgrade; old unit names may still be enabled. | M13, M14, M42 |
| Old `/usr/share/browneye`, `/var/lib/browneye` | Marker/state migration and cleanup. | M05, M07 |
| Old kernel cmdline `browneye.*`, labels and `BROWNEYE-ANSWER` | Accepted as aliases during the window while new installs write `tenko.*`/`TENKO*`. | M28, M30 |
| Historical `%changelog` entries | History; checkpoint 9 explicitly exempts them. | M38 |

### 1.9 Non-literal identifiers the grep does not see

These need the same treatment but do not contain the literal string
`browneye`, so they are absent from `occurrences.tsv`:

| Item | Current value | New value |
|---|---|---|
| R2 key prefix | `R2_PATH=${R2_PATH:-packages/$VERSION}` | `${R2_PATH:-tenko/packages/$VERSION}` |
| Public repo URL variable | `URL=${URL:-https://repo.pjfox.xyz/packages/$VERSION/}` | `https://repo.pjfox.xyz/tenko/packages/$VERSION/` |
| Installer default repo | `DEFAULT_REPO = "https://repo.pjfox.xyz/packages/13.1/"` | new `/tenko/packages/13.1/` URL |
| `build_iso_uefi.sh`, `make_base_image.sh`, `qemu_boot*.sh` repo defaults | `https://repo.pjfox.xyz/packages/13.1/` | new URL |
| `browneye-release` `baseurl=` | `https://repo.pjfox.xyz/packages/13.1/` | new URL |
| `README.md` public repository link | `https://repo.pjfox.xyz/packages/13.1/` | new URL |
| `web/index.html` package links | `packages/13.1/` | `tenko/packages/13.1/` |
| `spec-audit.md` curl commands | `https://repo.pjfox.xyz/packages/13.1/...` | new URL |
| `publish_repo.sh` / `publish_rpm.sh` mirror paths | `$MIRROR_PUBLIC/packages/$VERSION` | with `MIRROR_PUBLIC=public_html/tenko`, becomes `public_html/tenko/packages/13.1` |
| ISO/rootfs R2 directories | `iso/`, `rootfs/` | unchanged directories; new file names only |

### 1.10 Findings and decisions for checkpoint 2

1. **Historical changelogs conflict with the literal checkpoint-3 grep.**
   1,297 of 1,973 lines (66%) are history: 1,090 in the 419 changelog-only
   specs, 100 in the other 43 specs, 87 in the 13 renamed specs, and 20 in
   `docs/systemd-boot.md`'s pre-rename test record. Checkpoint 9 explicitly allows historical
   changelogs, so this inventory keeps them verbatim. The checkpoint-3
   verifier must either ignore `%changelog` sections (recommended) or use an
   explicit allowlist; otherwise it cannot pass without rewriting package
   history. If a literal clean grep is required, do the fake
   `browneye <build@browneye.invalid>` identity rewrite as a separate
   mechanical change after this checkpoint.
2. **`browneye-basefs` uses version 1.0.** Its Obsoletes is
   `browneye-basefs < 1.0-2`, not `< 13.1-2`.
3. **The LAN mirror has 15 extra RPMs.** They are superseded old versions plus
   `liblzo2-2.10-1`. Do not prune them during the window; `PRUNE=1` on the
   whole repository would remove files the compatibility story wants to keep.
4. **`iso/core.repo` is stale.** It points at
   `192.168.31.94/browneye/repos/0.3.5-rc1` and is copied by
   `scripts/build_rootfs.sh` and `scripts/install.sh`. Repoint it at the
   current Tenko repo or delete it; do not carry the old host forward.
5. **`%config(noreplace)` files need explicit cleanup.** The old
   `browneye-13.1.repo`, `/etc/dracut.conf.d/10-browneye.conf` and
   `/etc/systemd/journald.conf.d/10-browneye.conf` can survive an obsoleted
   package. The checkpoint-2 plan must remove or disable them in `%post`, and
   must disable/remove stale old units and presets on upgrade, not just on a
   clean install.
6. **Boot migration needs an ordering rule.** New kernel scriptlets write
   `tenko-<kver>.conf`; `loader.conf` may still default to `browneye-*` on an
   upgraded system. Write the new entry and update the default before removing
   the old entry. Old NVRAM labels remain until reinstall or manual cleanup.
7. **Container image fallback.** Scripts should prefer
   `localhost/tenko/base:r13.1` but fall back to
   `localhost/browneye/base:r13.1` until checkpoint 7 rebuilds the image.
8. **Repository/URL rename ordering.** Keep old Git/tracker/mirror links
   working until checkpoint 8. Scripts may be changed in checkpoint 3, but do
   not publish to the new R2 key or LAN path until checkpoint 5/6.
9. **No unknown dispositions.** Every one of the 1,973 matching lines has a
   mapping ID and a disposition in [`occurrences.tsv`](occurrences.tsv).

### 1.11 Reproduction

```sh
cd .worktrees/rename-tenko
git rev-parse HEAD

# Published repodata snapshot (baseline §0.3)
rclone copy r2:browneye/packages/13.1/repodata /tmp/tenko-baseline-repodata
sha256sum /tmp/tenko-baseline-repodata/repomd.xml
zstd -dc /tmp/tenko-baseline-repodata/*primary.xml.zst

# Occurrence scan (baseline §1.1)
grep -rIl --exclude-dir=.git --exclude=.git --exclude-dir=build -i browneye .
grep -rIin --exclude-dir=.git --exclude=.git --exclude-dir=build -i browneye . \
  | wc -l
```

The published repodata package list can be regenerated from
`baseline-packages.csv`; the per-line dispositions are in
`occurrences.tsv`.
