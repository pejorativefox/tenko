# Browneye Linux 13.1 — status

Last updated: 2026-11-03 (installer ISO boot + unattended install verified). Branch `lfs-r13.1`.
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
- **ntp-leap is published but not installable.**  `update-leap` needs the
  CPAN modules `IO::Socket::SSL` and `Net::SSLeay`, which are not in
  LFS/BLFS.  The main `ntp` package installs normally; decide whether to
  add specs for the two perl modules (not in the books, so a user call) or
  drop the subpackage.
- **Kernel 7.3.1 boot tests.**  The installer ISO boot, the unattended
  install, the installed-disk UEFI boot, the graphical LightDM greeter and
  an NVMe boot are verified (see the boot/install section below); qemu
  11.1.3-2 is installed on the host (daspork is in the `kvm` group; tool
  shells need `sg kvm -c ...`).  The direct `-kernel` boot is verified
  too (Linux 7.3.1 + dracut live initramfs -> multi-user -> login).  Still
  pending: logging into an XFCE session from the greeter (the greeter
  itself is captured).
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
  replaced by `pulsemixer`.  That is why the original 63 is now 61.  qemu
  was deferred during D7 and built later (see the qemu 11.1.3 section).
- **All of D7 is published** (76 packages plus the `ntp-leap` subpackage),
  taking the repo from 629 to 706 RPMs after verifying that all 76 install
  together from the published repo.

**Installer ISO and media**
- `build/browneye-installer.iso` is now **642 MiB** (was 1014 MiB), UEFI-only,
  kernel 7.3.1, with a 221-RPM on-ISO repository (was 263) that includes
  rpm 4.18.1-6 — installing from the media no longer yields a segfaulting
  dnf.  See the ISO size round below.
- `build_iso_uefi.sh` accepts an http(s) repo URL for the live root and
  passes the same URL to the installer; the EFI FAT image is authored
  inside the tools container (no host dosfstools).
- Every boot/ISO script and the installer dry-run fallback now default to
  KVER 7.3.1; `bootstrap_selfhosted.sh` globs the kernel RPMs.

**ISO size round (2026-11-03)**
- The install media no longer carries developer tools.  `browneye-installer`
  13.1-7 installs `browneye-base-runtime` instead of `browneye-base` and
  drops `opencode-bin`/`herdr` from its target set.  The on-ISO repo fell
  from 263 RPMs / 672 MiB to 221 RPMs / 323 MiB.
- **Network-only installs (2026-11-03, user decision).**  Installing and
  running a system requires an internet connection, so the media no longer
  carries any packages at all: `make_iso_repo.sh` is deleted,
  `build_iso_uefi.sh` ships no `/repo`, and `browneye-installer` 13.1-8
  installs from <https://tomfool.8bit.ca/browneye/packages/13.1/> by
  default (a URL or a local path can still be passed to `--repo`).  The
  post-install copy to `/var/lib/browneye/repo` and the
  `browneye-local.repo` file are gone with it.  The installer writes
  `browneye-13.1.repo` on the target with the source it used (13.1-12), so
  `dnf install` keeps working afterwards.
- HTTPS needs a trust store, which the runtime meta lacked: **browneye-base-runtime
  13.1-2** now requires `make-ca`, and **make-ca 1.16.1-3** only regenerates
  its bundle when it is missing.  In the ISO's restricted installroot the
  old %post ran make-ca without anchors and replaced the shipped bundle
  with an empty file, so the live environment had no CA certificates.
- `efiboot.img` shrank from 24 MiB to **12 MiB** (the smallest FAT16
  `mkfs.fat` accepts; it holds the 4.7 MiB `BOOTX64.EFI`).
- Net result: 1014 MiB -> **642 MiB** with the pruned on-ISO repo, then
  **323 MiB** once the media stopped carrying packages at all.  The live
  root has no gcc/make/git/podman/opencode/herdr and carries the fixed
  rpm.
- The ISO is published at
  <https://tomfool.8bit.ca/browneye/iso/browneye-installer.iso> (with a
  `.sha256` next to it) and at the LAN mirror
  <http://192.168.31.9/~daspork/browneye/iso/browneye-installer.iso>; it is
  linked from the repository overview and the packages index, and
  `gen_repo_index.py`/`publish_repo.sh` keep that link when they regenerate
  the index.
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

**qemu 11.1.3 and its book dependencies**
- The tree had a 2023 qemu 8.1.0 stub.  Updated to **11.1.3**, the BLFS
  r13.1 version, and published; the build follows the book
  (`--target-list=x86_64-softmmu`, `--sysconfdir=/etc`,
  `--audio-drv-list=alsa`, `--disable-pa`, `--disable-download`,
  `--enable-slirp`).  `qemu-bridge-helper` is setuid root:kvm (4750).
- New book dependencies, also built and published: **dtc 1.8.1** (libfdt)
  and **libslirp 4.9.7** (user-mode networking).  The build image used for
  qemu is `localhost/browneye/base:qemu-deps` (base + dtc + libslirp +
  alsa-lib).
- qemu installs the x86_64 system emulator, qemu-img/io/nbd/storage-daemon,
  the guest agent and tools, EDK2/vgabios firmware and keymaps (167 files,
  72 MiB RPM).  User-mode networking was smoke-tested (`-netdev user`
  starts, TCG); KVM is compiled in but needs /dev/kvm access.
- Two build snags fixed in the spec: the tools image lacked alsa-lib, and
  the generic brp-strip pass chokes on qemu's non-x86 ELF firmware blobs
  (palcode-clipper, hppa-firmware*.img), so `__brp_strip` is disabled for
  this package after the distro's own strip pass has run.

**Installer boot and install test (2026-11-03)**
- Booted the 642 MiB ISO under UEFI (QEMU's bundled EDK2) with KVM:
  GRUB -> dracut dmsquash-live -> multi-user, installer started, serial
  getty up.
- Added `tests/installer-answer.json` and built an auto-install ISO
  (`ISO_AUTO=1`, `browneye.auto=1`).  The unattended install into a 20 GiB
  virtio disk completes with `install-complete disk=/dev/vda` and
  `BROWNEY-INSTALL: OK`; the network-only flow was then re-verified: with
  `-nic user` the installer downloaded all 225 packages over HTTPS from
  the repository in ~9 minutes, the installed system booted, logged in as
  `admin`, reported `running`, had active swap, and `dnf repoquery` from
  the installed system resolved `bash-5.3` from the repo.
- The installed system boots from the disk and logs in over the serial
  console as `admin` (`uid=1000`, wheel), `systemctl is-system-running`
  reports **running**, swap (`/dev/vda2`, 2 GiB) is active and
  `systemctl --failed` is empty.
- Bugs found and fixed by this test:
  - **LVM2 2.03.44-2** - `lvm-devices-import.service` hardcoded
    `/usr/sbin/vgimportdevices` while the distro installs it in
    `/usr/bin`; the unit failed on every boot.
  - **linux-pam 1.7.3-3** - no PAM service files for the shadow
    utilities, so `chpasswd` could not set the admin password and
    `login`/`su`/`passwd` fell through to the deny-all `other` stack.
    Now ships login, su, passwd, chpasswd, newusers.
  - **systemd 262.1-2** - built with `-Dswapon-path=/usr/bin/swapon`
    (`swapoff` likewise); the default `/usr/sbin/swapon` does not exist
    here, so the installer's swap partition never activated.
  - ISO bootargs use `rd.overlay=1` (dracut 112 deprecates
    `rd.live.overlay.overlayfs`), and a stale `answer.json` is removed
    from the staging tree when `ISO_ANSWER` is unset.
- **Graphical boot:** the installed system comes up in
  `graphical.target`; LightDM is active, logind shows a class=`greeter`
  session on seat0, and a VNC screendump shows the Browneye LightDM
  greeter with the `admin` user.
- **Direct `-kernel` boot:** `qemu -kernel vmlinuz -initrd initramfs`
  with the ISO attached boots Linux 7.3.1, the dracut live initramfs
  mounts the squashfs and the system reaches multi-user with a login
  prompt - no GRUB or UEFI involved.
- **NVMe boot:** the same installed image attached as an NVMe namespace
  boots GRUB (`grubx64.efi` from the ESP) and reaches `browneye-test
  login:` - the initramfs carries the NVMe driver.  The installer registers
  its UEFI boot entry in the install VM's NVRAM, so on a fresh NVRAM the
  firmware falls back to the EFI shell; launching the removable
  `\EFI\BOOT\BOOTX64.EFI` works.
- **qemu 11.1.3-2:** the first build image had no pixman or libpng, so
  qemu was silently built without VNC (`-vnc: invalid option`) or PNG
  screendump.  pixman is a required BLFS dependency; both are now
  BuildRequires and VNC/PNG are enabled, which is what made the greeter
  screenshot possible.
- Test helpers added: `tests/installer-answer.json` and
  `tests/serial_login.py` (logs in on the installed system and runs the
  health checks).

**Environment**
- Host is Browneye 13.1 itself: 16 cores / 19 GB, rootless podman, gcc
  16.2.0, Python 3.15.2; `sudo` needs a password, use `unshare -r`.
- Repo: <https://tomfool.8bit.ca/browneye/packages/13.1/> (732 published
  files, including superseded NEVRAs).
- **LAN mirror:** every publish also updates
  `daspork@192.168.31.9:public_html/browneye`, served at
  <http://192.168.31.9/~daspork/browneye/>.  `publish_rpm.sh` and
  `publish_repo.sh` mirror automatically; the new `scripts/publish_iso.sh`
  uploads an ISO plus a fresh `.sha256` to both sites.  `MIRROR=0` skips
  the LAN copy (AGENTS.md rule).  The initial sync (732 RPMs + repodata +
  index + ISO) is done and verified with `dnf --repofrompath` against the
  mirror.
