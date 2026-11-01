# Handoff — browneye LFS r13.1 base rebuild

Last updated: 2026-11-01. Branch: `lfs-r13.1`. Work root: `~/browneye`.

Read this first. It supersedes the earlier wave-by-wave plan; the history is in
`git log` and the old text is no longer the source of truth.

---

## 1. TL;DR

**Item 1 (LFS version parity) is effectively complete for the base system.**

- **80/80** LFS chapter-8 systemd packages build from specs, including
  **grub 2.14**; the full base set is **93/93** specs (**94** RPMs, because
  glibc now ships a `glibc-locales` subpackage).
- `build/repo` is the old host-built repo and still contains stale versions;
  `build/repo-selfhost` is the clean repo produced by the container rebuild.
- `browneye-base` meta resolves and installs **94** packages into
  `build/rootfs` and `build/rootfs-selfhost`.
- The single base+desktop repo (218 RPMs) is staged in `build/repo-all`;
  `https://tomfool.8bit.ca/browneye/packages/13.1/` still has the previous
  217-RPM revision until the next publish (deferred at the user's request).
- The rootfs is QEMU-booted to multi-user and a serial root login; bash 5.3,
  python 3.14.7, openssl 4.0.2, merged `/usr`, loader at
  `/usr/lib64/ld-linux-x86-64.so.2`.

**Item 2 (build container) now has a working RPM toolchain.**

- Bootstrap image `localhost/browneye/base:r13.1-rpm5-20261030` exists (1.3 GB);
  final self-hosted image is
  `localhost/browneye/base:r13.1-selfhost-20261031`.
- Contains `rpm` 4.18.1 + `rpmbuild`, `browneye-rpm-config`, and the base
  toolchain. `rpm -qa` sees all 94 installed packages (sqlite rpmdb at
  `/usr/lib/sysimage/rpm`).
- Verified inside the container: build a C package with `rpmbuild -bb`,
  install it with `rpm -Uvh`, run it, remove it; and build `which-2.21`
  directly from `package_specs/`.
- `dnf` and `createrepo_c` are **not** in the image yet. The **build** is
  self-hosted; repo/rootfs **assembly** is still host-assisted (§6 E1).

**Self-hosted rebuild (2026-10-31).**

- All **93** specs in the base set (80 LFS + bootstrap extras + glue +
  `browneye-base`) build inside `browneye/base:r13.1-rpm5-20261030` with
  `--network=none`.
- The first full run exposed and fixed: host-Perl texinfo (`MiscXS.so`),
  missing pip, `makeinfo`-using packages, tcl's split-library path, ncurses
  `tinfo.pc`, gettext's C# assembly, grub's `/usr/sbin` payload, groff PDF
  generation without URW fonts, and sqlite's autosetup host-triplet compiler
  lookup.
- `scripts/bootstrap_selfhosted.sh` assembled `build/repo-selfhost` (97
  RPMs), installed `build/rootfs-selfhost` (93 packages), and built
  `localhost/browneye/base:r13.1-selfhost-20261031`.  The new image verified
  `pip 26.2.1`, `tclsh`, `makeinfo 7.3`, `/usr/sbin/init` owned by systemd,
  `gcc 16.2.0`, `rpmbuild 4.18.1`, and 93 installed packages.
- The second-generation full rebuild against that image passed **93/93**
  (`build/container-rebuild-selfhost-20261031/`).  The container can now
  rebuild every base package from its own RPMs, offline (`--network=none`).
- `bootstrap_selfhosted.sh` was run once more from the second-generation
  output, so the final `localhost/browneye/base:r13.1-selfhost-20261031`
  image, `build/repo-selfhost`, and `build/rootfs-selfhost` all come from
  self-hosted RPMs.  Smoke builds of `zlib` and `python-flit-core` pass in
  that image; `rpm -Va` is clean except podman's `/etc/hosts` overlay.

**C1–C6c and XFCE refresh (2026-10-31 → 11-01).**

- `build/container-rebuild-20261031-locale` rebuilt all **93** specs
  (**94** RPMs) offline against `r13.1-selfhost-20261031`.
  `bootstrap_selfhosted.sh` regenerated `build/repo-selfhost` (**98** RPMs),
  `build/rootfs-selfhost` (**94** packages), and the image.  The new rootfs
  carries the full glibc locale archive and the systemd chapter-9 defaults
  (presets applied, networkd/resolved enabled, empty machine-id).  C6b then
  replaced the base specs' directory globs with static filelists
  (`build/container-filelists-20261031`) and the run was re-bootstrapped.
  C6c synced the non-base X/GNOME chain to BLFS r13.1, built it offline in
  `build/blfs-parity-20261031`, and generated its filelists (LLVM 22.1.8
  with clang and compiler-rt).
- **XFCE 4.20 core (17 packages) builds X11-only** on that stack; Wayland is
  absent from the image by design.  Dependencies and the desktop build in
  `build/blfs-parity-20261031` (deps) and `build/blfs-parity-20261101`
  (desktop run).
- **The XFCE desktop now boots graphically.**  D4 adds the X11 runtime
  (Xorg 21.1.24, dbus, libinput, xinit, fonts) and the `xfce-desktop` meta;
  `scripts/qemu_boot_graphical.sh` boots it in QEMU and captures the session.
  The desktop ships in the **same** repository as the base
  (`https://tomfool.8bit.ca/browneye/packages/13.1/`).  Mesa 26.2.3
  (llvmpipe) is built and `xorg-server` now ships GLX/glamor, so the XFCE
  compositor is enabled (XRender on the VM; GLX on real GPUs).  Remaining
  visual gap: no SVG icon loader; see D4/D5 and §7.
- **Version parity reached (2026-11-01):** `scripts/audit_versions.py` reports
  no shipped package below the current LFS/BLFS trunk; `gtk2` was dropped and
  the remaining 127 "outdated" entries are specs the distro does not build.
- **Ready-to-boot test image:** `build/xfce-test.img` (base + `xfce-desktop`,
  kernel 7.2.6) starts the XFCE session on tty1; `scripts/qemu_run_desktop.sh`
  opens it in a GTK window or over VNC, with a serial console
  (`root`/`root`) and a QEMU monitor socket.  The old "crash a few seconds
  after the desktop loads" was `getty@tty1` failing and disallocating the VT;
  fixed in util-linux (§7) and the test image masks `getty@tty1`.
- **General kernel and firmware (2026-11-01):** `linux-kernel`/
  `linux-modules` **7.2.6-2** use the sanitized Fedora 44 config (3,030
  built-in / 4,691 modules, 4,849 xz-compressed module files).  The
  `linux-firmware` 20261019 curated subset (401 MB installed) plus
  wireless-regdb is required by `xfce-desktop`.  The XFCE screenshot and
  the UEFI GRUB disk boot were both re-tested with this kernel.

**Phase 2 boot smoke test is green (2026-10-30).**

- Kernel **7.2.6** (self-hosted) now uses the general sanitized config
  (D9); virtio-blk/virtio-pci/serial/ext4/9p/virtio-gpu are still built in,
  so the QEMU image boots without an initramfs.  Packages are
  `linux-kernel` and `linux-modules`; `linux-firmware` 20261019 (D10) is
  installed by the `xfce-desktop` meta-package.
- `scripts/qemu_boot.sh` installs the kernel into the rootfs, materializes
  sysusers, builds a raw ext4 image, and boots it under QEMU/KVM.
- Boot log: no `FAILED` units, `Reached target Multi-User System`, serial
  `login:` prompt, `Browneye Linux 13.1 / Kernel 7.2.6`.
- Interactive check passed: temporary root password, `root` login over
  `ttyS0`, `id` = `uid=0(root)`, `uname -a` = 7.2.6, then `poweroff -f`.
  The temporary password was restored; root is locked by default.
- Bootloader: **E3** adds a UEFI GRUB disk image that boots without
  `-kernel`.  The initramfs is still deferred to E4: the QEMU image uses
  built-in virtio/ext4, while real NVMe/LUKS/LVM roots need one.  Still
  missing: a real root password policy (E5).
- Re-booted `build/rootfs-selfhost` after C1/C3 (2026-10-31): **zero
  `FAILED` units**, `Reached target Multi-User System`, serial getty and
  networkd running, and systemd generated a machine-id on first boot
  (`ROOTFS=... ./scripts/qemu_boot.sh`).  The boot log is
  `build/qemu-boot-selfhost.log`.
- Re-tested 2026-11-01 with the general kernel + firmware: the graphical
  test image reached the XFCE session (screenshot
  `build/xfce-screenshot.png`), and the UEFI disk boot reached
  multi-user/login with zero `FAILED` units.  The only kernel log oddity is
  a cosmetic `CONFIG_DRM_PANIC_SCREEN='qr_code'` fallback warning inherited
  from the Fedora config.

---

## 2. Environment and layout

- Host: Fedora 44, x86_64, 16 cores / 32 GB, podman 5.8, dnf5, rpm 6.0.2,
  host gcc 16.2.1 / binutils 2.46.1. `sudo` requires a password; use
  `unshare -r` for anything needing fake root (see §5).
- Main checkout: `~/repos/browneye` on `master` (contains the merged
  `gcc-13-update` history).
- Work root: `~/browneye`, a git worktree on branch `lfs-r13.1`.
- Canonical Git remote: `ssh://pjfox-git/daspork/browneye.git` (Gitea at
  `https://pjfox.xyz/git/daspork/browneye`); `github` is a mirror remote.
  The `pjfox-git` SSH alias lives in `~/.dotfiles/ssh_config`.
- LFS/BLFS source of truth: the book checkouts `~/repos/lfs` and
  `~/repos/blfs` (branch `trunk`, the r13.1 line), as required by
  `AGENTS.md`.  The r13.1 tag (`71ef60ba`) predates several versions used by
  C13, so take versions from the checkouts, not the tag.
- Build outputs: `~/rpmbuild/{SOURCES,RPMS/x86_64,BUILD,...}`.
- `~/.rpmmacros` is installed from `rpmsupport/rpmmacros`.

### Layout

```
~/browneye/
├── bbuild                     # CLI: build/query
├── builder/                   # build.py, package.py, sources.py, db.py, ...
├── package_specs/             # 500+ specs; base set + glue
│   ├── ORDER                  # LFS chapter-8 order + browneye glue
│   └── sqlite/                # renamed from sqlite3
├── rpmsupport/
│   ├── rpmmacros              # installed to ~/.rpmmacros
│   └── strip_debug.sh
├── scripts/
│   ├── gen_lfs_lock.py        # regenerate lfs.lock from a tag
│   ├── sync_lfs_spec.py       # dry-run/--write version+source sync
│   ├── gen_filelist.py        # snapshot a built RPM into a %files list
│   ├── gen_filelist_tree.py   # snapshot an install tree (new version/file set)
│   ├── audit_versions.py      # RPM/spec versions vs the LFS/BLFS books
│   ├── book_source.py         # resolve/download a book source URL + md5
│   ├── prune_repo.sh          # keep the newest RPM per package
│   ├── make_efi_disk.sh       # GPT/UEFI GRUB disk image (no -kernel)
│   ├── publish_repo.sh        # stage + rsync repo to tomfool.8bit.ca
│   ├── build_blfs_stack.sh    # BLFS r13.1 X/GNOME/XFCE/desktop stack (phases)
│   ├── assemble_repo.sh       # base + non-base RPMs -> build/repo-all
│   ├── qemu_boot_graphical.sh # build/test the desktop image and capture it
│   ├── qemu_run_desktop.sh    # interactive XFCE test boot (GTK/VNC + serial)
├── lfs.lock                   # pinned versions/sources/patches/base list
├── Containerfile              # FROM scratch + rootfs tarball
├── web/index.html             # landing page for the published repo
└── build/
    ├── repo/                  # old host-built createrepo output (stale)
    ├── repo-selfhost/         # clean repo from the container rebuild (98 rpms)
    ├── rootfs/                # old installed base system
    ├── rootfs-selfhost/       # installed from repo-selfhost (94 packages)
    ├── browneye-rootfs.tar.gz # old image payload
    ├── container-rebuild-*/   # per-package logs/RPMs from verify runs
    ├── blfs-parity-*/         # non-base X/GNOME + XFCE + desktop builds
    ├── repo-all/              # base + desktop RPMs (217), the published repo
    ├── rootfs-desktop/        # installed base + xfce-desktop (graphical test)
    ├── rootfs-xfce-test/      # rootfs behind build/xfce-test.img
    ├── xfce-test.img          # ready-to-boot interactive XFCE test image
    ├── browneye-efi.img       # GPT/UEFI GRUB disk (E3), no -kernel
    ├── efi-work/              # ESP/root partitions used to build the disk
    └── deps/                  # extracted devel prefixes (see §5)
```

---

## 3. Decisions (still in force)

| # | Decision | Value |
|---|---|---|
| D1 | Init | **systemd 261.3** (book systemd variant) |
| D2 | Library layout | **`/usr/lib64`**, merged `/usr` via basefs symlinks |
| D3 | Kernel | **7.2.6**, self-hosted (E2), general config based on the Fedora 44 host kernel |
| D4 | Bootstrap | **chapter 8 self-hosted**; ch5–7 deferred (D2) |
| D5 | Book pin | **current LFS/BLFS checkouts** (trunk, r13.1 line); see `AGENTS.md` |
| D6 | Desktop | **XFCE 4.20** (BLFS r13.1), **X11 only**; not GNOME, zero Wayland |
| D7 | glibc patch | **upstream_fixes-3** (the book's `-2` is 404; user-approved) |
| D8 | Legacy GTK | **GTK2 dropped** (archive-only); `libcanberra` rebuilt GTK3-only |
| D9 | Kernel config | Sanitized Fedora 44 host config: debug info, SELinux/IMA, lockdown/signing, Rust/BTF, UBSAN and MAXSMP off; QEMU boot pieces built in |
| D10 | Firmware | **linux-firmware 20261019** curated subset (401 MB installed) + wireless-regdb 2026.09.03; `xfce-desktop` requires it |

Consequences already implemented:

- `package_specs/ORDER` is the chapter-8 systemd order (no sysvinit/sysklogd/udev).
- `browneye-basefs` owns `/bin /lib /lib64 /sbin` symlinks and the base dirs.
- `browneye-release` owns `/etc/os-release` + `/usr/lib/os-release`.
- `browneye-sysconfig` owns `/etc/{hosts,shells,inputrc,vimrc,profile}`.
- `browneye-base` requires the base set + `browneye-basefs/sysconfig/release`
  + `libbsd`, `libmd`, `libseccomp`. It excludes `grub`.

---

## 4. Reproduce the current state

### Build a package or batch

```bash
cd ~/browneye
./bbuild build zlib
./bbuild build grep sed tar coreutils --jobs 6
./bbuild build all --jobs 4        # ordered, but includes the whole tree
```

- `--jobs` parallelises package builds (auto = 8 on this box).
- Each `rpmbuild` gets `-j16` from rpm macros.
- Source downloads are 12-way.
- Output: `~/rpmbuild/RPMS/x86_64/`.

### Sync a spec to the pinned LFS version

```bash
./scripts/sync_lfs_spec.py pkg1 pkg2             # dry run
./scripts/sync_lfs_spec.py --write pkg1 pkg2     # mechanical edits only
./scripts/gen_lfs_lock.py --lfs-repo ~/repos/lfs --tag r13.1 --output lfs.lock
```

`--write` updates `Version`, `Source0`, the `sources` file, and changelog.
It flags old sonames/docdirs/patches that need manual edits.

### Refresh repo + rootfs + image

```bash
cd ~/browneye
cp ~/rpmbuild/RPMS/x86_64/*.rpm build/repo/
createrepo_c --quiet --update build/repo

rm -rf build/rootfs
unshare -r dnf -y --nogpgcheck \
  --installroot "$PWD/build/rootfs" --releasever=13.1 \
  --disablerepo='*' --repofrompath=browneye,file://$PWD/build/repo \
  --setopt=install_weak_deps=False --setopt=tsflags=noscripts \
  install browneye-base

unshare -r tar -C build/rootfs -czf build/browneye-rootfs.tar.gz .
podman build -t browneye/base:r13.1-$(date +%Y%m%d) .

podman run --rm browneye/base:r13.1-rpm5-20261030 /usr/bin/bash -lc \
  'bash --version | head -1; python3 -V; openssl version; rpmbuild --version'
```

`tsflags=noscripts` is required because the install runs as a fake root and
package scriptlets (ldconfig, systemd sysusers, shadow) fail without real root.

### Rebuild the RPM toolchain

`rpm` needs several of our own libraries as a build prefix. `bbuild` alone is
not enough; use the extracted prefixes under `build/deps/`:

```bash
cd ~/browneye
P=$PWD/build/deps/popt/usr; O=$PWD/build/deps/openssl/usr
F=$PWD/build/deps/file/usr; A=$PWD/build/deps/libarchive/usr
L=$PWD/build/deps/lua/usr;  E=$PWD/build/deps/libelf/usr
S=$PWD/build/deps/sqlite/usr
CPPFLAGS="-I$P/include -I$O/include -I$F/include -I$A/include -I$L/include -I$E/include -I$S/include" \
CFLAGS="$CPPFLAGS" \
LDFLAGS="-L$P/lib64 -L$O/lib64 -L$F/lib64 -L$A/lib64 -L$L/lib64 -L$E/lib64 -L$S/lib64" \
PKG_CONFIG_PATH="$P/lib64/pkgconfig:$O/lib64/pkgconfig:$F/lib64/pkgconfig:$A/lib64/pkgconfig:$L/lib64/pkgconfig:$E/lib64/pkgconfig:$S/lib64/pkgconfig" \
./bbuild build popt libarchive lua rpm browneye-rpm-config

# rpm links libdw if the host headers are visible; libdw is not needed when
# debuginfo is disabled:
#   export ac_cv_header_elfutils_libdwelf_h=no   (already in rpm.spec)
```

The rpm spec uses:

```
--without-lua --without-python --without-selinux --without-cap --without-acl
--without-readline --disable-plugins --disable-nls --enable-libelf=yes
--enable-sqlite=yes --with-crypto=openssl
```

`rpm` itself still needs Lua at runtime (for its macro engine), so `lua` is a
runtime dependency even though Python bindings are disabled.

### Build a package inside the container

```bash
podman run --rm \
  -v "$PWD/package_specs/which:/spec:ro,Z" \
  -v "$HOME/rpmbuild/SOURCES:/sources:ro,Z" \
  browneye/base:r13.1-rpm5-20261030 \
  /usr/bin/bash -lc \
  'rpmbuild -bb --define "_sourcedir /sources" /spec/which.spec'
```

RPMs land in `/rpmbuild/RPMS/<arch>/` inside that container (rpm 4.18's
default `_topdir`). Compile, install, and remove them in the same container to
test the full cycle:

```bash
rpmbuild -bb /tmp/chello.spec
rpm -Uvh --nodeps /rpmbuild/RPMS/x86_64/chello-1.0-1.x86_64.rpm
rpm -q chello && /usr/bin/chello && rpm -e chello
```

### Rebuild the whole base inside the container

This is the self-hosting check. The host only creates the package list and
bind-mounts specs, sources, and output; every `rpmbuild` runs in the image.

```bash
cd ~/browneye
OUT=build/container-rebuild-$(date +%Y%m%d-%H%M%S) \
  ./scripts/verify_base_in_container.sh

# failed package names + log tails
./scripts/show_rebuild_failures.sh build/container-rebuild-YYYYMMDD-N
```

The wrapper mounts with `:z` (shared SELinux label), not `:Z`: starting a
second container with `:Z` relabels the shared `package_specs` tree and makes
a running rebuild fail with `Permission denied` on every later spec.

Bootstrap steps happen inside the container before the parallel queue:

1. **texinfo** is rebuilt first and installed into the throw-away container.
   The old image's texinfo was built on the host with Perl 5.42, but the image
   ships Perl 5.44; its `MiscXS.so` cannot load and every `makeinfo` caller
   (dejagnu, binutils, gcc, ...) fails. The rebuilt texinfo is installed with
   `rpm -Uvh --replacepkgs --replacefiles`.
2. **tcl** is rebuilt next and installed the same way. The old image's
   `tclsh8.6` was built with `/usr/lib/tcl8.6` compiled in but the library was
   moved to `/usr/lib64/lib/tcl8.6`; sqlite's autosetup/configure needs a
   working `tclsh`. The rebuilt tcl adds `/usr/bin/tclsh` and a
   `/usr/lib/tcl8.6` compatibility symlink, and packages its `tzdata`.
3. **pip** is bootstrapped with `python3 -m ensurepip` because the current
   image was built with `--without-ensurepip`. The Python module specs also
   use `--no-build-isolation --ignore-installed`, so they build offline and
   do not try to uninstall the rpm-owned copy in the running image. The
   rebuilt python spec installs pip from the bundled wheel into the RPM
   buildroot, so the next image does not need this bootstrap.

After the rebuild, assemble a clean repo and next-generation image:

```bash
./scripts/bootstrap_selfhosted.sh build/container-rebuild-YYYYMMDD-N
# creates build/repo-selfhost, build/rootfs-selfhost,
# build/rootfs-selfhost.tar.gz, and
# localhost/browneye/base:r13.1-selfhost-YYYYMMDD

IMAGE=localhost/browneye/base:r13.1-selfhost-YYYYMMDD \
  OUT=build/container-rebuild-selfhost \
  ./scripts/verify_base_in_container.sh
```

`bootstrap_selfhosted.sh` refuses to run if any status file says `fail`.
It copies only RPMs produced by the container rebuild; the phase-2 kernel
RPMs are copied from `~/rpmbuild` as an optional boot payload and are not
part of `browneye-base`.  It then materializes sysusers, applies
`systemctl --root=/ preset-all` in the new rootfs, packs it, and builds the
container image.

### Publish the repo

```bash
cd ~/browneye
./scripts/publish_repo.sh
# -> https://tomfool.8bit.ca/browneye/packages/13.1/
```

The script stages `build/repo-all` into `build/repo-publish/13.1`, runs
`scripts/prune_repo.sh` first so only the newest RPM of each package is
published, runs `createrepo_c`, writes `browneye-13.1.repo` and
`README.txt`, and rsyncs with `--delete` to
`tomfool8@192.200.112.194:public_html/browneye/packages/13.1/` (SSH port
53211; the `ssh_tomfool` alias in `~/.bashrc.d/ssh_alias.sh` matches).  The
repo is unsigned (`gpgcheck=0`).  It also uploads `web/index.html` to
`browneye/` and generates a per-version `index.html` listing (the web server
has directory indexes off).  Landing page:
<https://tomfool.8bit.ca/browneye/>.

### Rebuild the non-base BLFS stack

The X/GNOME stack used by the non-base filelists builds in a persistent
container so each RPM's dependencies are visible to the next package:

```bash
cd ~/browneye
KEEP=0 PHASE=core      ./scripts/build_blfs_stack.sh  # X libs, GLib/GI, GTK3 (GTK2 removed)
KEEP=1 PHASE=rest      ./scripts/build_blfs_stack.sh  # curl, libuv, cmake, libjpeg, ImageMagick, LLVM
KEEP=1 PHASE=xfce-deps ./scripts/build_blfs_stack.sh  # XFCE 4.20 dependencies
KEEP=1 PHASE=xfce      ./scripts/build_blfs_stack.sh  # 17 XFCE 4.20 core packages
KEEP=1 PHASE=desktop   ./scripts/build_blfs_stack.sh  # Xorg, input, drivers, fonts, meta
```

`PHASE=core` includes the two-pass GLib build (first without introspection so
`gobject-introspection` can link against it, then again with GI data).  The
script skips packages already marked `ok` in `build/blfs-parity-*/status`, so
it is resumable.  XFCE is built X11-only: `libxfce4windowing` gets
`--enable-x11 --disable-wayland`, and no Wayland libraries are installed.
Pass `OUT=build/blfs-parity-YYYYMMDD` to keep a multi-phase run in one place
(the default is date-stamped).  The container mounts `/out` at creation time,
so a resumed run keeps writing RPMs to the first `OUT` even if a new `OUT` is
passed; status/logs follow the new one.

Assemble, publish, and boot the desktop:

```bash
./scripts/assemble_repo.sh                # base + non-base RPMs -> build/repo-all
RSYNC_OPTS=-c ./scripts/publish_repo.sh   # -> packages/13.1/ (base + desktop)
./scripts/qemu_boot_graphical.sh          # desktop rootfs + X session + xwd capture
./scripts/qemu_run_desktop.sh             # interactive test boot (GTK/VNC + serial)
```

`qemu_run_desktop.sh` builds `build/xfce-test.img` on first use.  That image
masks `getty@tty1` (the one-shot X service owns tty1) and uses a temporary
`root`/`root` password; it is a test image, not the distro default.

### Boot the rootfs under QEMU

```bash
cd ~/browneye
./bbuild build linux                  # once, ~5-10 min
./scripts/qemu_boot.sh                # installs kernel + modules, boots
```

`qemu_boot.sh` does:

1. copies the self-hosted `linux-kernel`/`linux-modules` from
   `build/repo-all` into `build/repo`;
2. `dnf --installroot build/rootfs install linux-kernel linux-modules`;
3. runs `systemd-sysusers` and `systemctl --root=/ preset-all` inside the
   rootfs (install scriptlets were skipped);
4. runs `depmod -b` (kernel module scriptlets were skipped);
5. `mke2fs -d build/rootfs` → `build/rootfs.img` (3 GB);
6. boots with `root=/dev/vda console=ttyS0` and logs to `build/qemu-boot.log`.

`ROOTFS`, `IMG`, and `LOG` can be overridden in the environment, e.g. to boot
`build/rootfs-selfhost`; `/etc/machine-id` is left empty so systemd generates
one on first boot.

Expected tail:

```
[  OK  ] Reached target Multi-User System.
...
Browneye Linux 13.1
Kernel 7.2.6 on an x86_64 (ttyS0)
localhost login:
```

`timeout 180` kills QEMU on purpose (exit 124). Check
`grep -a FAILED build/qemu-boot.log`; it should be empty.

### Boot the UEFI disk image (no `-kernel`)

```bash
cd ~/browneye
./scripts/make_efi_disk.sh                 # -> build/browneye-efi.img
cp /usr/share/OVMF/OVMF_VARS.fd build/OVMF_VARS.fd
qemu-system-x86_64 -enable-kvm -cpu host -m 3072 -smp 4 \
  -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE.fd \
  -drive if=pflash,format=raw,file=build/OVMF_VARS.fd \
  -drive file=build/browneye-efi.img,format=raw,if=virtio \
  -display gtk -serial file:/tmp/efi-serial.log
```

`make_efi_disk.sh` builds a GPT disk (64 MiB FAT ESP + ext4 root), writes a
standalone `grub-mkstandalone` `BOOTX64.EFI`, and sets
`root=(hd0,gpt2)` / `root=/dev/vda2`.  The grub package is EFI-only (BLFS
builds `--with-platform=efi`); BIOS boot would need the `i386-pc` modules.
No initramfs is used because virtio-blk and ext4 are built into the
kernel; NVMe, SCSI and USB-storage are modules, so a real hardware root
needs the E4 initramfs.

---

## 5. Critical gotchas

1. **`sudo` needs a password.** Use `unshare -r` for rpm root-dir tests,
   dnf installroot, and tarballing files with mode 000 (`/etc/shadow`).
   `unshare -r true` works here.
2. **dnf is dnf5** — `-v` is invalid; use `--setopt=debuglevel=10` or
   `rpm --root ... --test` inside `unshare -r` to see conflicts.
3. **`~/.rpmmacros` is required.** It sets `_libdir=/usr/lib64`, disables
   debuginfo/build-id, disables `check-rpaths`, and defines `%strip`.
   `bbuild` prepends `rpmsupport/` to `PATH` so `strip_debug.sh` resolves.
   `strip_debug.sh` only strips writable files (perl ships read-only `.so`).
4. **Host contamination is the main failure mode.** Fedora has devel packages
   LFS does not. We disabled extras in these specs:
   - `glibc`, `coreutils`, `findutils`, `sed`, `tar`, `gettext`, `dbus`:
     `--without-selinux` (dbus: `-D selinux=disabled`)
   - `coreutils`: `--without-openssl`
   - `gettext`: `--with-included-libxml`
   - `kmod`: `-D openssl=disabled`
   - `kbd`: `--disable-xkb`
   - `vim`: `--without-wayland --disable-selinux`
   - `iproute2`: runs `./configure`, then `sed -i "/selinux/Id" config.mk`
   - `glibc`/`gcc`/`grub`: override `CFLAGS/LDFLAGS` to avoid Fedora
     `-flto`/hardening (`export CFLAGS="-O2 -g"; export LDFLAGS=""`)
   If a new package fails to resolve in the rootfs with "nothing provides
   libfoo.so", it was linked against a host library. Rebuild it with the
   matching `--without-*` or against the built deps prefix.
5. **Devel prefixes for host build deps:** `build/deps/` holds extracted
   headers/libs from our own RPMs:
   - `expat/` — needed by `python`, `dbus`
   - `openssl/`, `sqlite/` — needed to link `python` to our 4.0/3.53 ABI
   - `libmd/` — needed by `libbsd`
   - `py/` — jinja2/markupsafe for systemd's meson check
   - `popt/`, `file/`, `libarchive/`, `lua/`, `libelf/` — RPM toolchain
     build prefixes (see §4 “Rebuild the RPM toolchain”)
   Rebuild commands (examples):
   ```bash
   E=$PWD/build/deps/expat/usr; O=$PWD/build/deps/openssl/usr; S=$PWD/build/deps/sqlite/usr
   CPPFLAGS="-I$E/include -I$O/include -I$S/include" \
   CFLAGS="-I$E/include -I$O/include -I$S/include" \
   LDFLAGS="-L$E/lib64 -L$O/lib64 -L$S/lib64" \
   LD_LIBRARY_PATH="$E/lib64:$O/lib64:$S/lib64" \
   PKG_CONFIG_PATH="$E/lib64/pkgconfig:$O/lib64/pkgconfig:$S/lib64/pkgconfig" \
   ./bbuild build python

   PYTHONPATH=$PWD/build/deps/py/usr/lib64/python3.14/site-packages \
   ./bbuild build systemd
   ```
6. **Python module specs** use `pip install --root=... --prefix=/usr` with
   build isolation (network access) and move `/usr/lib/python3.14` to
   `/usr/lib64`. `python3-setuptools` is installed in the user site.
7. **`%files` are intentionally broad** in many base specs (`/usr/bin/`,
   `/usr/lib64/`, etc.). This was done to get to a working base quickly.
   Tightening them is deferred debt.
8. **`build/repo` still contains stale RPMs** from earlier versions
   (`zlib-1.2.13`, `sqlite3`, debuginfo). Clean it before publishing.
9. **`lfs.lock` aliases** map LFS names to spec names; `sqlite` was renamed
   from `sqlite3` and the alias removed. `pcre -> pcre2`,
   `libelf -> elfutils`, `procps -> procps-ng`, `flit-core -> python-flit-core`,
   etc.
10. **Old scripts are stale:** `scripts/install.sh`, `build_rootfs.sh`,
    `build_iso*.sh`, `podman_build.py`, `create_root_filesystem.sh` still
    assume the old finit/`/usr -> .` hack and the unreachable
    `192.168.31.94` repo. Do not use them for the current flow.
11. **The RPM toolchain needs build prefixes.** `rpm` links `popt`, `libelf`,
    `sqlite`, `libarchive`, `libmagic`, `liblua`, and OpenSSL 4. The exact
    env is in §4 “Rebuild the RPM toolchain”. `--enable-libelf=yes` is
    required for automatic ELF `Requires`/`Provides`; without it `rpmdeps`
    silently emits no library dependencies. `--enable-sqlite=yes` is
    required so the container's rpm reads the rpmdb written by the host dnf
    (path `/usr/lib/sysimage/rpm`, set by `browneye-rpm-config`).
12. **Kernel headers come from the kernel source.** `linux-api-headers`
    7.2.6 runs `make headers` and copies the sanitised `usr/include` tree
    from the linux-7.2.6 source; the file set matches `headers_install`
    (1078 entries) without needing `rsync`.  It is required to compile
    anything that includes `<limits.h>`/`<linux/limits.h>`.  C13 rebuilt
    glibc and the UAPI consumers against it.
13. **`rpm` owns `/rpmbuild` by default.** The container writes build trees
    under `/rpmbuild` (not `/build`). Mount sources read-only and copy RPMs
    out, or change `%_topdir` in `browneye-rpm-config` deliberately.
14. **LLVM installs into `/usr/lib`, not `/usr/lib64`.**  Mesa's
    `libgallium` depends on `libLLVM.so.23.1` there, so `xorg-server` needs
    `-Wl,-rpath-link,/usr/lib`, and image builds must add `/usr/lib` to
    `/etc/ld.so.conf` and run `ldconfig`.  See §7 for the clean fix.
15. **Static filelists need care when versions change.**  Regenerate them
    from the populated buildroot with `scripts/gen_filelist_tree.py` (it
    quotes paths with spaces and lists symlinked directories as files, not
    `%dir`).  Do not repackage with `rpmbuild --short-circuit`: the RPM
    carries an unsatisfiable `rpmlib(ShortCircuited)` requirement.  Rebuild
    normally after generating the list.

---

## 6. What remains

### A. Item 2 bootstrap (DONE)

- [x] A1. Build `rpm` 4.18.1 (upstream installs `rpmbuild` in the same
      package; no separate `rpm-build` split was needed).
- [x] A2. Add `rpm` + `popt` + `libarchive` + `lua` + `linux-api-headers` to
      `browneye-base`; refreshed repo/rootfs/image.
- [x] A3. Repo tooling decision: **keep `createrepo_c` on the host** for now.
      A `createrepo_c` spec is still missing; building it needs curl/glib/
      libxml2/rpm devel and is not required for `rpmbuild`.
- [x] A4. dnf decision: **do not build dnf yet.** Use host dnf for repo/rootfs
      assembly and `rpm -Uvh --nodeps` inside the container for incremental
      installs. Revisit for a fully self-hosted pipeline.
- [x] A5. `browneye-rpm-config` now installs
      `/usr/lib/rpm/macros.d/macros.browneye` (`_libdir=/usr/lib64`,
      `_dbpath=/usr/lib/sysimage/rpm`, debuginfo off, check-rpaths off,
      bytecompile errors non-fatal) and
      `/usr/lib/rpm/browneye/strip_debug.sh`.
- [x] A6. Verified inside `browneye/base:r13.1-rpm5-20261030`:
      `rpmbuild --version` = 4.18.1, `_libdir` = `/usr/lib64`,
      `rpm -qa | wc -l` = 93, C package build/install/run/remove works, and
      `which-2.21` builds from `package_specs/` with ELF auto-requires.

### B. Close the last base package

- [x] B1. `grub 2.14` now builds in the self-hosted container.  The host
      failure was Fedora toolchain/LTO/cross detection; the container build
      installs everything under `/usr/bin` because rpm's `_sbindir` is
      `/usr/bin` there, and that is reflected in `%files`.  E3 now builds a
      UEFI disk image with GRUB and boots it without `-kernel`.

### C. Remaining base hardening before phase-2 boot

- [x] C1. `glibc-locales` subpackage: `make localedata/install-locales`
      installs the full `localedata/SUPPORTED` set as a single
      `/usr/lib/locale/locale-archive` (223 MB, 886 locales).  It builds
      offline in the container, is required by `browneye-base`, and the
      installed rootfs reports 888 entries from `locale -a`;
      `de_DE.UTF-8` and `ja_JP.UTF-8` were checked at runtime.
- [x] C2. QEMU boot test: kernel 7.2.6 + ext4 rootfs boots to multi-user and
      a serial login prompt. `scripts/qemu_boot.sh` is the direct-kernel
      path; `scripts/make_efi_disk.sh` is the GRUB/UEFI path (E3).  The
      initramfs is deferred to E4 because all storage drivers are built in.
- [x] C3. systemd chapter-9 config: `browneye-sysconfig` now ships
      `/etc/locale.conf` (`LANG=C.UTF-8`), `/etc/vconsole.conf`
      (`KEYMAP=us`), an empty `/etc/machine-id` (systemd generates one on
      first boot), `/etc/resolv.conf` → `/run/systemd/resolve/stub-resolv.conf`,
      `/etc/systemd/journald.conf.d/10-browneye.conf` (persistent journal,
      512M cap), and `/etc/systemd/network/10-dhcp.network` (DHCP=yes on
      `en*`/`eth*`).  `bootstrap_selfhosted.sh` and `qemu_boot.sh` run
      `systemctl --root=/ preset-all`, which enables networkd, resolved,
      timesyncd, getty, oomd, and the other unit presets (42 symlinks in the
      fresh rootfs).  `serial-getty@ttyS0` and `default.target` remain
      explicit symlinks; udev rules ship from systemd in
      `/usr/lib/udev/rules.d` with an empty `/etc/udev/rules.d` override dir.
- [x] C4. `/etc/passwd`/`group`/`shadow` baseline: root and system users
      exist through `systemd-sysusers`; a temporary-password root login over
      `ttyS0` was tested (`LOGIN_OK`, `uid=0`, kernel 7.2.6). Root is locked
      again after the test; E5 tracks a first-boot password/account policy.
- [x] C5. Clean repo: `build/repo-selfhost` is the canonical clean,
      self-hosted repo (97 RPMs, no stale/debuginfo entries).  The old
      `build/repo` is retained only as historical bootstrap output and is not
      used by the new flow.
- [x] C6a. Base static filelists regenerated: `tcl` (including tzdata and
      symlinks) and `groff` (removed PDF/URW-only entries); `kbd`'s existing
      filelist builds unchanged.
- [x] C6b. Base `%files` tightened: 21 specs that used top-level directory
      globs now use generated static filelists.  `scripts/gen_filelist.py`
      snapshots the current build's paths, `%dir` entries, and
      `%config`/`%doc` flags.  Verified by rebuilding all 21 offline and
      diffing `rpm -qlp` against the previous build: file sets are identical
      except that the shared top-level dirs (`/etc`, `/var`, `/var/cache`,
      `/var/lib`) are no longer owned.  Non-base `glib` was regenerated too
      (447 entries, unchanged).
- [x] C6c. *(Historical versions; C13 brought these to current.)* Non-base
      stack synced to BLFS r13.1 and rebuilt offline in a persistent
      container (see `scripts/build_blfs_stack.sh`): X libraries
      (`xorgproto` 2025.1 through `libXtst` 1.2.5, `libXft` 2.3.9), `pixman`
      0.46.4, `libpng` 1.6.58, `libjpeg-turbo` 3.2.0, `freetype` 2.14.3,
      `fontconfig` 2.18.3, `harfbuzz` 14.3.1, `fribidi` 1.0.16, `glib`
      2.88.3 (two-pass GObject Introspection), `gobject-introspection`
      1.86.0, `cairo` 1.18.4, `at-spi2-core` 2.60.6, `gdk-pixbuf` 2.44.7,
      `pango` 1.58.2, `libepoxy` 1.5.10, `libxkbcommon` 1.13.2,
      `shared-mime-info` 2.5.1, `libxml2` 2.15.3, `gtk2` 2.24.33,
      `gtk3` 3.24.52, `imagemagick` 7.1.2, `curl` 8.21.0, `libuv` 1.52.1,
      `cmake` 4.4.2, `llvm` 22.1.8 (with clang and compiler-rt).  Generated
      static filelists for the whole chain; all of the named targets except
      LLVM were rebuilt with their filelists to verify (the LLVM list is a
      snapshot of a successful build; rebuilding it costs ~35 min).
- [x] C7. Removed every stale disabled spec: `browneye-basefs-nousr`,
      `browneye-init`, `libwnck2`, `lxterminal`, `python2-urlgrabber`,
      `sysvinit`, `valgrind`, `webkitgtk`, `yum`.  Their directories (and
      `webkitgtk/sources`) are gone; no `.disabled` files remain.
- [x] C8. Two-phase order documented: `package_specs/ORDER` stays
      chapter-8 + bootstrap extras, and `scripts/verify_base_in_container.sh`
      appends `libbsd`, `libmd`, `libseccomp`, and `browneye-base` for the
      full 93-package run.
- [x] C9. `linux-api-headers` is now generated from the pinned
      **linux-7.1.8** tarball (`make headers`, then copy the sanitised
      `usr/include` tree).  The file set is identical to the
      `headers_install` output (1085 entries) and no longer needs `rsync` in
      a clean build image.  Rebuilt the UAPI consumers against it: `glibc`
      2.44 with `glibc-locales`, `systemd` 261.2, `util-linux` 2.42.2,
      `kmod` 34.2, `iproute2` 7.1.0, `e2fsprogs` 1.47.4, `procps-ng` 4.0.7,
      `shadow` 4.20.2, `libcap` 2.78, `libseccomp` 2.6.0.  The base repo now
      ships `linux-api-headers-7.1.8` (the host-derived 7.2.4 RPM is gone).
      The glibc spec regained its `%files locales` section (`locale-archive`).
      *Superseded by C13:* headers are now 7.2.6 (1078 entries) and the
      consumers above were rebuilt again against them.
- [x] C12. **Version parity audit and rule.** `scripts/audit_versions.py`
      compares every RPM in `build/repo-all` and every spec against the
      LFS/BLFS entities and reports outdated packages.  The rule is recorded
      in `AGENTS.md`: update the package and its dependency chain to at least
      the book versions before building, and ask before substituting anything
      not in LFS/BLFS.  The initial audit found 36 built packages below the
      books and 127 non-built spec-only entries; C13 closed the former.
      `scripts/gen_filelist_tree.py` rebuilds a static `%files` list from an
      install tree, and `scripts/book_source.py` resolves/downloads a book
      source with its md5.
- [x] C13. **Bring the built set to book versions (parity wave) — done 2026-11-01.**  The audit
      found these shipped packages below LFS/BLFS trunk:
      *base:* `linux-api-headers` 7.1.8→7.2.6, `openssl` 4.0.1→4.0.2,
      `xz` 5.8.3→5.8.4, `pcre2` 10.47→10.48, `elfutils` 0.195→0.196,
      `systemd` 261.2→261.3, `iproute2` 7.1.0→7.2.0, `automake` 1.18.1→1.19,
      `pkgconf` 3.0.5→3.0.7, `lua` 5.4.6→5.4.8, `vim` 9.2.1025→9.2.1099,
      `man-pages` 6.18→6.19, `iana-etc` 20260805→20260911;
      *desktop:* `glib` 2.88.3→2.90.0, `at-spi2-core` 2.60.6→2.62.0.1,
      `cairo` 1.18.4→1.18.6, `cmake` 4.4.2→4.4.3, `curl` 8.21.0→8.22.0,
      `fribidi` 1.0.16→1.0.17, `gdk-pixbuf` 2.44.7→2.44.8,
      `harfbuzz` 14.3.1→14.5.0, `hwdata` 0.410→0.411,
      `libarchive` 3.7.1→3.8.9, `libevdev` 1.13.6→1.13.7,
      `libinput` 1.31.3→1.32.0, `libseccomp` 2.6.0→2.6.1,
      `libtirpc` 1.3.7→1.3.8, `libuv` 1.52.1→1.53.0,
      `libwnck` 43.1→43.3, `libxfont2` 2.0.6→2.0.9,
      `libxml2` 2.15.3→2.15.4, `rsync` 3.5.0→3.5.1,
      `thunar` 4.20.9→4.20.10, `upower` 1.91.3→1.91.4.
      Order: headers → glibc → its consumers → the rest of the base → a
      fresh base rootfs, then the desktop libraries (glib first) and a
      desktop rootfs/image rebuild.  `sqlite`'s `3530400` entity is the
      autoconf form of 3.53.4 and is already current.  The 127 other
      spec-only "outdated" entries are packages the distro does not build
      (GNOME/Bluetooth/CUPS/ffmpeg/…); they only need updating if they are
      ever built.
- [x] C11. Close the self-hosting gaps found by rebuilding the base inside the
      container: rebuild texinfo/tcl before their users, bootstrap pip, and
      install the new RPMs into a fresh rootfs/image.  The fresh image rebuilt
      all 93 packages offline in the second-generation run.
- [ ] C10. Add an initramfs (dracut in the target or a custom cpio).
      **Deferred to E4:** the 7.2.6 QEMU config builds `VIRTIO_BLK`,
      `BLK_DEV_NVME`, `SATA_AHCI`, `SCSI`, `USB_STORAGE`, and `EXT4_FS`
      in (`=y`), so the GRUB disk image boots without an initramfs (E3).
      An initramfs is only needed once E4 switches to a general-purpose
      modular config.  No dracut package is in the current BLFS book, so a
      custom cpio is the intended route.


### D. Phase 2 (D3 done; D2 remains out of current scope)

- [x] D1. Kernel packaging: `linux-kernel`/`linux-modules` **7.2.6** with the
      QEMU config, now built inside the self-hosted container (E2).
- [ ] D2. Chapters 5–7 self-hosted toolchain as bootstrap RPMs.
- [x] D3. **XFCE 4.20 core built, X11 only, zero Wayland.**  All 17 core
      packages build offline on the C6c stack: `libxfce4util`, `xfconf`,
      `libxfce4ui`, `exo`, `garcon`, `xfce4-dev-tools`,
      `libxfce4windowing`, `xfce4-panel`, `xfwm4`, `xfce4-session`,
      `xfce4-settings`, `thunar`, `thunar-volman`, `tumbler`,
      `xfce4-appfinder`, `xfdesktop`, `xfce4-power-manager`.  Dependencies
      built too: `libwnck` 43.1, `libdisplay-info` 0.4.0, `libgudev` 238,
      `libnotify` 0.8.8, `upower` 1.91.3, `polkit` 127 (shadow auth, no PAM),
      `startup-notification`, `libxklavier`, `libcanberra`,
      `desktop-file-utils` 0.28, `libexif`, `duktape`, `iso-codes` 4.20.1,
      `libvorbis`/`libogg`, `libusb`, `libxslt`, `iceauth`, plus the X
      libraries.  `libxfce4windowing` is configured
      `--enable-x11 --disable-wayland`; the container has **no Wayland
      libraries or packages**.  Generated static filelists for the whole
      XFCE set and rebuilt all 17 packages with them.
- [x] D4. **X11 runtime and graphical boot, X11 only.**  Added and built:
      `dbus` 1.16.2 (system + session bus, systemd units), `xorg-server`
      21.1.24 (meson; `-Dglamor=true -Dglx=true -Ddri3=true
      -Dsuid_wrapper=true -Dsystemd_logind=false`), X libraries (`libxcvt` 0.1.3, `libtirpc`
      1.3.7, `libpciaccess` 0.19, `libdrm` 2.4.134, `libxfont2` 2.0.6,
      `libXt` 1.3.1, `libXmu` 1.3.1, `xkbcomp` 1.5.0), input (`libevdev`
      1.13.6, `mtdev` 1.1.7, `libinput` 1.31.3, `xf86-input-libinput`
      1.5.0), `xf86-video-vesa` 2.3.3, `xkeyboard-config` 2.48, `xinit`
      1.4.4, `xauth` 1.1.5, `xrdb`/`xset`/`xmodmap`/`xhost`/`xwininfo`/`xwd`,
      fonts (`font-util` 1.4.2, `encodings` 1.1.0, `font-alias` 1.0.6,
      `font-bh-ttf` 1.0.4), `hicolor-icon-theme` 0.18, and an `upower`
      rebuild that installs its systemd unit.  New specs: `xfce-desktop`
      (meta) and `browneye-desktop-config` (`/etc/X11/xinit/xinitrc` →
      `startxfce4`; xinit now ships that file, `%config(noreplace)`-style).
      `scripts/qemu_boot_graphical.sh` boots a fresh desktop rootfs under
      QEMU/KVM with `-vga std`, starts X on tty1 through a one-shot
      `xfce-test.service`, and captures the session with `xwd` over a 9p
      share (the QEMU std-VGA screendump is blank with modesetting).
      Verified: `xfce4-session`, `xfwm4`, `xfce4-panel`, `xfdesktop`,
      `xfsettingsd`, `xfce4-power-manager`, `dbus`, `xfconf`, panel and dock
      all running; panel 1280x27 at the top and the launcher dock at the
      bottom.
- [x] D4b. **Mesa and GLX, X11 only.**  `libxshmfence` 1.3.3, `expat`
      2.8.4, `LLVM` 23.1.0 (self-hosted, filelist regenerated from the
      buildroot), and `mesa` 26.2.3 (`-Dplatforms=x11
      -Dgallium-drivers=llvmpipe -Dvulkan-drivers= -Dglx=dri
      -Dglvnd=disabled`; no Wayland/Vulkan) are built.  `xorg-server` was
      rebuilt with GLX/DRI3 and its filelist regenerated; `libglx.so`,
      `libglamoregl.so`, and the DRISWRAST provider load.  The test image
      enables `use_compositing` and boots with kernel 7.2.6
      (`DRM_VGEM`, `DRM_BOCHS`, `DRM_VIRTIO_GPU`).  On the VM, modesetting
      refuses glamor on llvmpipe and xfwm4 blacklists llvmpipe for its GLX
      compositor, so compositing uses XRender; a GLX client still gets a
      working llvmpipe renderer.  `xf86-video-amdgpu` can now build (gbm is
      present) but is not packaged yet.
- [x] D5. **One published repository (base + desktop).**  There is no
      separate desktop repo.  `scripts/assemble_repo.sh` collects the base
      repo plus every BLFS/XFCE/desktop RPM into `build/repo-all` (217
      RPMs, newest version per package); `scripts/publish_repo.sh` publishes it to
      `https://tomfool.8bit.ca/browneye/packages/13.1/` with the usual
      `browneye-13.1.repo`.  `xfce-desktop` installs from the same baseurl,
      and the landing page documents it.

### E. Self-hosting and boot follow-ups (open)

These are the current caveats that do not yet have a checkbox elsewhere.

- [ ] E1. Build `dnf`/`libdnf` + `createrepo_c` (and their dependency stack)
      and move repo/rootfs assembly into the self-hosted image. Today
      `scripts/bootstrap_selfhosted.sh` still calls host `dnf`/`createrepo_c`
      (see A3/A4 and §7).
- [x] E2. `linux-kernel`/`linux-modules` **7.2.6** are now built inside the
      self-hosted container (with `DRM_VGEM`) and collected into the single
      repo; the host-built 7.1.8 RPMs are gone.  E4 still covers firmware,
      signing, and the general-purpose config.
- [x] E3. **GRUB disk boot works (UEFI).**  `scripts/make_efi_disk.sh` builds a
      GPT image: a 64 MiB FAT ESP with a standalone `BOOTX64.EFI`
      (`grub-mkstandalone`, ext2/linux/part_gpt modules), and an ext4 root
      partition populated from the installed rootfs.  GRUB sets
      `root=(hd0,gpt2)` and loads `vmlinuz-7.2.6` with
      `root=/dev/vda2`; QEMU boots it with OVMF and no `-kernel`, reaching
      multi-user and a serial login.  The grub spec is EFI-only (BLFS builds
      `--with-platform=efi`), so BIOS boot needs i386-pc modules that are not
      built; the image also needs no initramfs because virtio/ext4 are
      built in.  C10 still covers an initramfs for hardware whose storage
      drivers are modules.
- [ ] E4. The general-purpose config and firmware are done (D9/D10); the
      initramfs generator and module signing remain.  The config keeps
      virtio-blk/ext4/9p/virtio-gpu built in for the initramfs-less QEMU
      boot.
- [ ] E5. Add a first-boot root password/account policy. The login test used
      a temporary password and restored the locked shadow entry.

---

## 7. Known technical debt

- The first-generation base was built against the **host** (Fedora 44)
  compiler and libraries. The second-generation rebuild inside
  `r13.1-selfhost-20261031` passed 93/93, but `bbuild` on the host remains a
  useful fast path and can reintroduce a host-only `DT_NEEDED`. Always verify
  with a container rebuild and reinstall the rootfs after adding packages.
- The base set and `glib` use generated static filelists; upstream file
  additions now fail the build (intended).  The non-base X/GNOME chain is
  synced to BLFS r13.1 and also uses generated filelists (C6c).
- GTK2 was removed from the distro (it is archive-only in BLFS): the spec
  and RPM are gone and `libcanberra` is built without its GTK2 module.
  XFCE 4.20 is GTK3-only.
- `libepoxy` is built with GL/EGL headers copied from the host into the
  throwaway container (it `dlopen`s libGL at runtime, so the RPM has no
  dependency on a host library).  `gdk-pixbuf` keeps the PNG loader because
  the BLFS default relies on glycin, which is not in the base.
- `curl` is built with `--without-libpsl` (libpsl is not in the base); CMake
  only needs curl for its own network features.
- `scripts/build_blfs_stack.sh` defaults `OUT` to `build/blfs-parity-$(date)`.
  The XFCE build crossed midnight, so its statuses are split between
  `blfs-parity-20261031` and `blfs-parity-20261101`; pass `OUT=...` to keep a
  run together.
- `browneye-base` has 93 `Requires:` (generated from `lfs.lock` plus the
  manual bootstrap list); it is not regenerated automatically when versions
  change.
- The repo is unsigned.  `scripts/prune_repo.sh` keeps the newest RPM per
  package, so the published repo has one version per name.
- The 218-RPM staging tree (`build/repo-all`, including kernel 7.2.6-2 and
  firmware 20261019-2) is ready but **not published yet**: the remote still
  has the previous 217-RPM revision.  Publish on request.
- Rootfs installs use `--setopt=tsflags=noscripts`; scriptlet correctness has
  not been tested outside the fake-root install.
- The container image is rootless/local (`localhost/browneye/base:...`) and
  not pushed anywhere.
- `package_specs/browneye-release` currently owns `/etc/os-release` as a
  symlink into `/usr/lib`; verify package ownership if you change it.
- `linux-api-headers` is generated from the 7.2.6 kernel source with
  `make headers` + `cp -a usr/include` (no rsync needed); the resulting file
  set is 1078 entries.
- The RPM toolchain (`rpm`, `libarchive`, `lua`, `popt`) was initially built
  against host devel prefixes (`build/deps/*`), but the second-generation
  rebuild compiled it inside the self-hosted image. Ch5–7 bootstrap is still
  absent; the container relies on the chapter-8 toolchain.
- The container has no `dnf`/`createrepo_c`; host tools are required to
  assemble a new rootfs or refresh the repo. The **build** is self-hosted;
  the **assembly** is still host-assisted.
- `build/repo` is not pruned: 111 RPMs include old versions, debuginfo from
  early builds, and both `sqlite` and the retired `sqlite3` name.
- The kernel (`linux-kernel`/`linux-modules` **7.2.6**) is built in the
  container (E2) and collected from `build/blfs-parity-*/build/linux`; the
  old host-built 7.1.8 RPMs are gone.
- The kernel config is a sanitized forward-port of the Fedora 44 host
  config (3,030 built-in / 4,691 modules after the QEMU overrides), not
  the old 6.4.12 minimal config.  Debug info, SELinux/IMA, lockdown and
  module signing, Rust/BTF, UBSAN and MAXSMP are off.  There is still no
  initramfs and no module signing (E4).
- `linux-firmware` is a curated 20261019 snapshot (GPUs, wireless,
  Bluetooth, Realtek NICs, AMD microcode) plus wireless-regdb 2026.09.03,
  401 MB installed and xz-compressed.  It is not a book package; the user
  approved a curated snapshot because BLFS only documents firmware.  The
  tarballs live in `~/rpmbuild/SOURCES`; URLs and sha256 are in the spec
  changelog.
- The kernel modules are xz-compressed at install, so kmod must be built
  with xz support (ours reports `+XZ`).  `CONFIG_MODULE_COMPRESS_XZ` alone
  is not enough on 7.2: `CONFIG_MODULE_COMPRESS_ALL` must also be enabled.
- The Fedora config leaves `CONFIG_DRM_PANIC_SCREEN="qr_code"` without the
  QR-code option, so boot logs one cosmetic fallback warning; set it to
  `user` or disable `CONFIG_DRM_PANIC` on the next rebuild.
- The kernel spec copies `arch/x86/boot/bzImage` directly instead of using
  `make install`; the latter tried to write a systemd-boot entry to the host
  `/boot/efi` during rpmbuild.
- `scripts/qemu_boot.sh` uses `unshare -r` for `mke2fs -d` because
  `/etc/shadow` and `/etc/gshadow` are mode 000.
- The QEMU login test used a temporary SHA-512 root password, then restored
  the locked shadow entry. There is no first-boot password setup or account
  policy yet.
- `systemd` is configured with `importd=disabled`, `remote=disabled`, and
  `imds=disabled` so the base build does not depend on `curl`; as a result
  `systemd-journal-remote` is not shipped.  The static filelist was
  regenerated for that configuration.
- **Mesa on llvmpipe:** `mesa` 26.2.3 and GLX are present, but the VM has no
  GPU.  `modesetting` logs "Refusing to try glamor on llvmpipe" and falls
  back to shadowfb; `xfwm4` blacklists llvmpipe for its GLX compositor and
  uses XRender instead.  This is expected for software rendering and does
  not affect real GPUs.  `xf86-video-amdgpu` can now build (gbm exists) but
  is not packaged yet.
- **Library directory split:** `llvm` installs into `/usr/lib` while the rest
  of the distro uses `/usr/lib64`.  `xorg-server` needs
  `-Wl,-rpath-link,/usr/lib` to link against `libgallium`, and the image
  build adds `/usr/lib` to `/etc/ld.so.conf` and runs `ldconfig`.  The clean
  fix is to build LLVM with `LLVM_LIBDIR_SUFFIX=64` (or move `libLLVM` into
  `/usr/lib64`).
- **Parity deviations:** glibc uses `upstream_fixes-3` because the book's
  `-2` patch is 404 (user-approved); `rsync` is built with `--disable-idn`
  because no `libidn2` headers are built; the lua 5.4.8 shared-library patch
  is the 5.4.6 file renamed (identical md5; the book's 5.4.8 URL is 404);
  `gdk-pixbuf` keeps PNG/JPEG and no glycin (no Rust).  The audit reports
  0 outdated built packages; 127 spec-only entries remain for packages the
  distro does not build.
- **No SVG loader:** `gdk-pixbuf` is built with `glycin` disabled and
  `librsvg` is absent, so SVG icons/wallpapers do not render.  The hicolor
  PNG icons from XFCE work (`hicolor-icon-theme` is required by the meta).
- **`/usr/sbin` compatibility:** `util-linux` installs `agetty`/`nologin` in
  `/usr/bin` (rpm `_sbindir`), but systemd's `getty@.service` and the
  `sysusers` shell default use `/usr/sbin/…`.  The spec now creates
  `/usr/sbin/agetty` and `/usr/sbin/nologin` symlinks.  Without them getty
  fails and restarts with `TTYVTDisallocate=yes`, which switches the console
  off tty1 and kicks X off its VT (looks exactly like a session crash).
  The graphical test image masks `getty@tty1.service` because its one-shot X
  service owns tty1; serial getty works normally.
- **No display manager:** `startx` (xinit) starts `startxfce4`; `lightdm`
  needs Linux-PAM, which the base does not have, plus a PAM-enabled systemd
  rebuild.
- The QEMU std-VGA `screendump` is blank with the modesetting driver, so
  `qemu_boot_graphical.sh` captures the root window with `xwd` over a 9p
  share (the debug unit also dumps `ps`, `xwininfo -root -tree`, the journal,
  and `Xorg.0.log` into `build/qemu-share/`).
- `xkeyboard-config` 2.48 emits "Could not resolve keysym ..." warnings with
  `xkbcomp` 1.5.0; they are non-fatal.
- The graphical test uses a one-shot `xfce-test.service` and a temporary
  root password; it is not a login/account policy (E5).
- `polkit` 127 is built with `authfw=shadow` (no Linux-PAM in the base) and
  `libnotify` is built with `-Dtests=false` (its tests pull GTK4).
- `xfce4-session` needs `iceauth` and `xfce4-dev-tools` needs `libxslt`;
  both are built as XFCE build dependencies.  BLFS r13.1's `libwnck` 43.1
  checksum is stale; the actual tarball md5 is used.
- `/etc/machine-id` is deliberately shipped empty and mode 0444; systemd
  generates/commits one on first boot. `qemu_boot.sh` no longer pre-fills it.
- The journal is persistent (`/var/log/journal`, 512M cap) and the network
  default is DHCP on `en*`/`eth*` via networkd/resolved. Both are distro
  policy choices rather than LFS requirements.
- The full C1/C3 run (`build/container-rebuild-20261031-locale`) built 93
  specs, but `browneye-sysconfig` was rebuilt separately in
  `build/container-sysconfig-20261031` (same self-hosted image, offline) and
  substituted into the run output; remeasure with a fresh full run when
  convenient.

---

## 8. Suggested next actions

1. **C10 + E4 — initramfs and module signing.**  The general config and
   firmware are in place; generate a custom-cpio initramfs for NVMe/LUKS/LVM
   roots and decide the module-signing/Secure Boot story.  Then boot the
   UEFI disk image with the initramfs.
2. **E1 — self-hosted repo/rootfs assembly.** Build `dnf`/`libdnf` and
   `createrepo_c` (plus dependencies) inside the container so assembly no
   longer needs host tools.
3. **Desktop polish and account policy.** SVG icons need Rust
   (`librsvg`/`glycin`); a display manager (`lightdm`) needs Linux-PAM and a
   PAM-enabled systemd rebuild; E5 needs a first-boot root
   password/account policy.  D2 (chapters 5–7 bootstrap RPMs) remains the
   largest self-hosting gap.

---

## 9. Useful one-liners

```bash
# audit every shipped RPM/spec against the LFS/BLFS books
python3 scripts/audit_versions.py | head -40

# keep one (newest) version per package in the repo
./scripts/prune_repo.sh build/repo-all

# what base packages are missing from the repo?
python3 - <<'PY'
import json, glob, os, subprocess
lock=json.load(open('lfs.lock')); names=set()
for p in glob.glob('build/repo-all/*.rpm'):
    if 'debug' in os.path.basename(p): continue
    try: names.add(subprocess.check_output(['rpm','-qp','--qf','%{NAME}',p],text=True))
    except Exception: pass
def present(n):
    c=lock['canonical_names'].get(n,n); s=lock['aliases'].get(n,n)
    return c in names or s in names or n in names
print([n for n in lock['base_packages'] if not present(n)])
PY

# inspect base meta requirements
rpm -qpR build/repo-all/browneye-base-13.1-1.x86_64.rpm | sort

# find host-contaminated requires across the repo
for r in build/repo-all/*.rpm; do rpm -qpR "$r" 2>/dev/null | grep -qE 'libselinux|libxml2|libwayland|libxkbcommon|libcrypto\.so\.3|libssl\.so\.3' && basename "$r"; done
```
