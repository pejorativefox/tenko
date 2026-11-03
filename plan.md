# Browneye Linux 13.1 — status

Last updated: 2026-11-03 (ISO size round: 1014 -> 642 MiB). Branch `lfs-r13.1`.
Work root `~/browneye`.
Detailed history is in `git log` (one commit per wave); rules are in
`AGENTS.md` (LFS/BLFS version parity, subagent worktrees).

---

## 1. Not finished

- **D3. Repository signing.**  Deferred by decision: the repo is unsigned
  (`gpgcheck=0`, `repo_gpgcheck=0`) and the ISO is UEFI-only and unsigned,
  so Secure Boot firmware rejects it.  Doing this means a signing key,
  signing at publish time, exporting the public key to installed systems,
  enforcing signature checks in the repo files, and signing the ISO.
- **qemu 11.1.3.**  Deferred on request (2026-11-03).  It is the only D7
  package that was not built; ffmpeg and everything else is done.
- **ntp-leap is published but not installable.**  `update-leap` needs the
  CPAN modules `IO::Socket::SSL` and `Net::SSLeay`, which are not in
  LFS/BLFS.  The main `ntp` package installs normally; decide whether to
  add specs for the two perl modules (not in the books, so a user call) or
  drop the subpackage.
- **Kernel 7.3.1 boot tests.**  `linux` 7.3.1-1 is built, published and
  carried by the installer ISO, but the three boot tests are still
  pending: QEMU is not installed on the host and the qemu 11.1.3 spec is
  deferred, so run them when a VM is available.  The rebuilt 642 MiB ISO
  (runtime-base target set) needs the same boot/install test.
- **Offline repo copy.**  `/var/lib/browneye/repo` is still the old
  259-RPM set.  A 706-RPM copy (sha256-verified, metadata regenerated,
  staged before rpm 4.18.1-6, bwm-ng and bash-completion; the published
  repo is now 712) is
  at `build/repo-all`; `/var/lib` is root-owned, so it needs one
  privileged command:
  `sudo rsync -a --delete build/repo-all/ /var/lib/browneye/repo/`.
- **librsvg typelib split (D6 leftover).**  The only typelib still in its
  runtime package (~9 KB).  Now possible because Rust 1.99 is installed.
- **Decisions that are not tasks:** `libbsd`/`libmd` stay as distro glue
  (book-less, required only by the base metas; user decision 2026-11-03);
  `podman-bin` is a static bundle (not rebuildable, invisible to CVE
  tracking); console/tty logins get no `pam_systemd` (no
  `/etc/pam.d/login`); `vte` vendors simdutf/fmt/fast_float as offline
  wraps; `unzip`'s spec still references a patch that 404s upstream.

---

## 2. Summary of the work already done

**Base system (LFS r13.1, systemd)**
- 93 chapter-8 specs build offline (`--network=none`) in a self-hosted
  container, producing 94 RPMs (glibc also ships `glibc-locales`).
- Boots to multi-user/serial login three ways (direct `-kernel`, UEFI GRUB
  disk, dracut initramfs on NVMe) with zero failed units.
- Kernel 7.2.6-5, glibc 2.44-3 with curated locales, systemd 262.1,
  merged `/usr` with `/usr/lib64`.  `browneye-base` requires are generated
  from `lfs.lock` and include `make-ca` (Mozilla trust store).

**Desktop**
- XFCE 4.20 on X11 only; Xorg 21.1.25, Mesa 26.2.3 (llvmpipe + virgl),
  LightDM + GTK greeter, AccountsService, sudo, VTE 0.84.1, xfce4-terminal
  1.2.0, librsvg 2.63.4 with the gdk-pixbuf SVG loader.
- kitty 0.49.2 is available as the official prebuilt `kitty-bin` bundle
  (self-contained Python/GL stack, static kitten, X11 only; no libssh or
  Wayland extras).

**Version parity (D9) and packaging**
- Every published package was re-baselined to the current LFS/BLFS trunk:
  glibc, openssl 4.1.0, systemd 262.1, Python 3.15.2, rpm/dnf stack,
  glib/harfbuzz/GTK, git, openssh, X11, Rust/cargo-c/librsvg, etc.
- Post-audit wave (2026-11-03): **706 RPMs published, 0 outdated**, one
  newer (`xml-parser 2.59` vs book 2.57).  Bumped `freetype` 2.15.0,
  `icu4c` 79.1 (filelists/sonames regenerated), `python-flit-core` 4.2.0,
  `python-markupsafe` 3.0.4, `python-setuptools` 84.2.1 and `linux` 7.3.1.
- `lfs.lock` is regenerated from LFS trunk `1493db7`; `sync_lfs_spec.py
  --all-base` now reports 80/80 up-to-date instead of proposing downgrades.
- The retired `system-minimal` RPM was pruned from the published repo and
  the duplicate `package_specs/libgcr` (the shipped gcr is 3.41.2) removed.
- Added `kitty-bin` 0.49.2 (prebuilt bundle) to the repo, taking it to 706
  RPMs; it installs its own Python 3.14/GL stack under `/opt/kitty-0.49.2`.
- User-approved exceptions outside the books: Google Chrome
  (`google-chrome-bin`), `pulsemixer` (replaces pavucontrol), three extra
  fonts, `podman-bin`, `linux-firmware`, `kitty-bin` (official prebuilt
  0.49.2 bundle; the source chain needs book-less xxhash/simde/slang/Go).
- `scripts/publish_rpm.sh` refuses re-publishing an existing NEVRA with
  different content (bump Release); `PRUNE=1` drops superseded files.

**Build images and self-hosting (S2, E2)**
- `scripts/make_base_image.sh` builds images from the published repo with
  no pre-existing image: `base:r13.1` (dnf-capable tool image, 147 pkgs),
  `base:r13.1-e2` (lean, no dnf stack, 121 pkgs) and
  `base:r13.1-selfhost-20261102` (108 pkgs installed only from the rebuild).
- E2 rebuilt the whole base set from scratch: **101/101 specs, 190 RPMs,
  zero failures**, then installed a rootfs exclusively from those RPMs;
  the result self-hosts (gcc 16.2.0, rpm 4.18.1, pip works).

**D7 (specs below the book): done**
- 61 of 61 in-scope packages brought to the book versions, built and
  verified: X11 libs, net-tools/sysklogd/acpid/ntp, libnl/libndp/libevent/
  libssh2/stunnel/wget/screen, glibmm/atkmm/pangomm/cairomm/libsigc++,
  vala, adwaita-icon-theme, newt/slang, imlib2/glew/freeglut/icewm,
  json-glib/appstream-glib/glib-networking/xdg-dbus-proxy,
  bubblewrap/iptables, nss/nspr, ntp, enchant/aspell, flac/libsndfile,
  NetworkManager + nm-applet (gnupg/libsecret/gcr/libnma), ruby, cups,
  pulseaudio + alsa-plugins, ffmpeg, gstreamer/gst-plugins-base,
  fuse3/pipewire and xdg-desktop-portal.
- pavucontrol was dropped (it now needs the whole GTK4 bindings stack) and
  replaced by `pulsemixer`; qemu was deferred.  That is why the original
  63 is now 61.
- **All of D7 is published** (76 packages plus the `ntp-leap` subpackage),
  taking the repo from 629 to 706 RPMs after verifying that all 76 install
  together from the published repo.

**Installer ISO and media**
- `build/browneye-installer.iso` is now **642 MiB** (was 1014 MiB), UEFI-only,
  kernel 7.3.1, with a 221-RPM on-ISO repository (was 263) that includes
  rpm 4.18.1-6 — installing from the media no longer yields a segfaulting
  dnf.  See the ISO size round below.
- `build_iso_uefi.sh`/`make_iso_repo.sh` accept an http(s) repo URL and
  resolve the ISO closure with `dnf install --downloadonly` from an empty
  installroot (the host does not have the dnf download plugin); the EFI
  FAT image is authored inside the tools container (no host dosfstools).
- Every boot/ISO script and the installer dry-run fallback now default to
  KVER 7.3.1; `bootstrap_selfhosted.sh` globs the kernel RPMs.

**ISO size round (2026-11-03)**
- The install media no longer carries developer tools.  `browneye-installer`
  13.1-7 installs `browneye-base-runtime` instead of `browneye-base` and
  drops `opencode-bin`/`herdr` from its target set; `make_iso_repo.sh`
  mirrors that set (runtime base, XFCE, kernel/modules, boot tooling, dnf,
  sudo) plus the five ISO authoring tools its own tools container installs.
  The on-ISO repo fell from 263 RPMs / 672 MiB to **221 RPMs / 323 MiB**.
- `efiboot.img` shrank from 24 MiB to **12 MiB** (the smallest FAT16
  `mkfs.fat` accepts; it holds the 4.7 MiB `BOOTX64.EFI`).
- Net result: 1014 MiB -> **642 MiB** (-37%).  The live root now has no
  gcc/make/git/podman/opencode/herdr and carries the fixed rpm.
- Tested and rejected: excluding `/usr/include`, man/doc/info and
  `gir-1.0` from the squashfs saved only ~6.7 MiB.
- **Follow-up found:** 10 `*-devel` packages (~2.9 MiB) are still pulled
  into every closure because runtime libraries ship `.pc` files and the RPM
  `pkgconfig` generator turns them into runtime `Requires: pkgconfig(...)`
  (e.g. `libdnf` -> `pkgconfig(rpm)` -> `rpm-devel`).  The fix is to move
  the `.pc` files into `-devel` subpackages; it would also remove the 16 MiB
  `/usr/include` from the live root.

**Tooling added**
- `scripts/bump_to_book.py` (book version/md5 → spec+sources),
  `scripts/regen_files.py` (static `%files` from BUILDROOT),
  `scripts/build_specs.sh` (build an arbitrary spec list in a container),
  plus the base-image, container-build, self-host and publish scripts.
- Repository metadata check: every published RPM's server size was
  compared against `primary.xml`.  Four X11 font RPMs (encodings,
  font-alias, font-bh-ttf, font-util) had been overwritten under the same
  NEVRA; they were rebuilt at release 2 and republished.  A full sweep
  now reports zero mismatches.

**rpm 4.18.1-6: dnf segfaults fixed**
- `dnf list installed`, `dnf info`, `dnf list --all` and `dnf history`
  crashed with SIGSEGV inside `vsnprintf` (rpmlog).  rpm 4.18's sqlite
  backend installed a *process-global* `SQLITE_CONFIG_LOG` handler that
  dereferences the `rpmdb` passed as user data.  The hook is global, so it
  also fired for libdnf's later `/var/lib/dnf/history.sqlite` connection
  after the rpmdb had been closed, and rpmlog formatted the freed
  `rdb->db_descr`; the crash path was
  `Swdb::Swdb` → sqlite3_exec → sqlite3_log → rpmlog → vsnprintf.
- Fixed with a backport of upstream commit `d018e756b72c` ("Don't muck
  with per-process global sqlite configuration from the db backend",
  patch `rpm-4.18.1-sqlite-global-log.patch`).  rpm 4.18.1-6,
  python3-rpm 4.18.1-6 and rpm-devel 4.18.1-6 are published (repo: 709
  RPMs); the four crashing commands were verified in the tools container
  before and after the upgrade (139 → 0).
- Bootstrap note: `dnf upgrade` itself is one of the crashing commands,
  so an installed system must take the fixed rpm with
  `sudo rpm -Uvh rpm-4.18.1-6 python3-rpm-4.18.1-6 rpm-devel-4.18.1-6`
  (download them from the repo) once, after which dnf works normally.

**bwm-ng 0.6.3**
- The tree had a 0.6.2 stub (TODO summary/description, never built or
  published).  Updated to upstream 0.6.3 (2021-01-10), built with
  `--with-ncurses` (the tarball is a git archive with no `configure`, so
  `autogen.sh` generates it) and published; repo is now 710 RPMs.
- bwm-ng is not in LFS or BLFS r13.1; the user approved 0.6.3 as the
  version-parity exception.  Verified in the tools container: binary runs
  against `/proc/net/dev`, links `libncursesw.so.6`, man page installed.

**bash-completion 2.18.0**
- The tree had a 2.10 stub (TODO summary/description, never built).  Updated
  to upstream 2.18.0 and published (repo 710 -> 711 RPMs); bash-completion is
  not in LFS or BLFS r13.1 (only listed as an optional dependency), so this
  is the user-approved version-parity exception.
- Configured with `--sysconfdir=/etc`, so the profile snippet lands in
  `/etc/profile.d/bash_completion.sh` where `/etc/profile` sources it (the
  2.10 stub installed it into `/usr/etc`, which nothing reads).
- 1118 files/symlinks, tracked by a generated static filelist
  (`package_specs/bash-completion/files/bash-completion.filelist`).  Verified
  in the tools container: `BASH_COMPLETION_VERSINFO=2 18 0` after login, and
  lazy loading works for tar/ssh/rpm/systemctl; dnf keeps its own completion
  from the dnf package.

**Environment**
- Host is Browneye 13.1 itself: 16 cores / 19 GB, rootless podman, gcc
  16.2.0, Python 3.15.2; `sudo` needs a password, use `unshare -r`.
- Repo: <https://tomfool.8bit.ca/browneye/packages/13.1/> (712 RPMs).
