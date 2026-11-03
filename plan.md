# Browneye Linux 13.1 — status

Last updated: 2026-11-03 (post-audit book-parity wave). Branch `lfs-r13.1`.
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
- **Kernel 7.3.1 boot tests.**  `linux` 7.3.1-1 is built and published
  (`linux-kernel`, `linux-modules`, `linux-kernel-debug`), matching the
  book.  The three boot tests are still pending: QEMU is not installed on
  the host and the qemu 11.1.3 spec is deferred, so run them when a VM is
  available.
- **Offline repo copy.**  `/var/lib/browneye/repo` on installed systems is
  still the old 259-RPM set; it does not contain the D9 wave, Chrome,
  cups/nss/nspr, pulseaudio or the D7 packages.  Regenerate it from the
  current 706-RPM repo when an ISO or offline install is next built.
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

**Tooling added**
- `scripts/bump_to_book.py` (book version/md5 → spec+sources),
  `scripts/regen_files.py` (static `%files` from BUILDROOT),
  `scripts/build_specs.sh` (build an arbitrary spec list in a container),
  plus the base-image, container-build, self-host and publish scripts.

**Environment**
- Host is Browneye 13.1 itself: 16 cores / 19 GB, rootless podman, gcc
  16.2.0, Python 3.15.2; `sudo` needs a password, use `unshare -r`.
- Repo: <https://tomfool.8bit.ca/browneye/packages/13.1/> (706 RPMs).
