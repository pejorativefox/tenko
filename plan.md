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
- The base repo is published at
  `https://tomfool.8bit.ca/browneye/packages/13.1/` (unsigned).
- The rootfs is QEMU-booted to multi-user and a serial root login; bash 5.3,
  python 3.14.7, openssl 4.0.1, merged `/usr`, loader at
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
  The desktop repo is published at
  `https://tomfool.8bit.ca/browneye/packages/13.1/desktop/`.  Remaining
  visual gaps: no Mesa (no libGL/GLX/compositing) and no SVG icon loader;
  see D4/D5 and §7.

**Phase 2 boot smoke test is green (2026-10-30).**

- Kernel **7.1.8** built with virtio-blk/virtio-pci/serial/ext4 built in;
  packages are `linux-kernel` and `linux-modules`.
- `scripts/qemu_boot.sh` installs the kernel into the rootfs, materializes
  sysusers, builds a raw ext4 image, and boots it under QEMU/KVM.
- Boot log: no `FAILED` units, `Reached target Multi-User System`, serial
  `login:` prompt, `Browneye Linux 13.1 / Kernel 7.1.8`.
- Interactive check passed: temporary root password, `root` login over
  `ttyS0`, `id` = `uid=0(root)`, `uname -a` = 7.1.8, then `poweroff -f`.
  The temporary password was restored; root is locked by default.
- Still missing: bootloader, initramfs, and a real root password policy.
- Re-booted `build/rootfs-selfhost` after C1/C3 (2026-10-31): **zero
  `FAILED` units**, `Reached target Multi-User System`, serial getty and
  networkd running, and systemd generated a machine-id on first boot
  (`ROOTFS=... ./scripts/qemu_boot.sh`).  The boot log is
  `build/qemu-boot-selfhost.log`.

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
- LFS source of truth: `~/repos/lfs`, pinned to tag **r13.1** (`71ef60ba`).
  Do not read versions from the working tree (it is trunk/r13.1+16).
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
│   ├── publish_repo.sh        # stage + rsync repo to tomfool.8bit.ca
│   ├── build_blfs_stack.sh    # BLFS r13.1 X/GNOME/XFCE/desktop stack (phases)
│   ├── assemble_desktop_repo.sh # base + non-base RPMs -> build/repo-desktop
│   ├── qemu_boot_graphical.sh # boot the XFCE desktop and capture it
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
    ├── repo-desktop/          # base + desktop RPMs (215), published as .../desktop
    ├── rootfs-desktop/        # installed base + xfce-desktop (graphical test)
    └── deps/                  # extracted devel prefixes (see §5)
```

---

## 3. Decisions (still in force)

| # | Decision | Value |
|---|---|---|
| D1 | Init | **systemd 261.2** (book systemd variant) |
| D2 | Library layout | **`/usr/lib64`**, merged `/usr` via basefs symlinks |
| D3 | Kernel | **7.1.8 packaged for QEMU**; self-hosted kernel rebuild tracked as E2 |
| D4 | Bootstrap | **chapter 8 self-hosted**; ch5–7 deferred (D2) |
| D5 | LFS pin | **r13.1 tag** (`71ef60ba`) |
| D6 | Desktop | **XFCE 4.20** (BLFS r13.1), **X11 only**; not GNOME, zero Wayland |

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

The script stages `build/repo-selfhost` into `build/repo-publish/13.1`, runs
`createrepo_c`, writes `browneye-13.1.repo` and `README.txt`, and rsyncs to
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
KEEP=0 PHASE=core      ./scripts/build_blfs_stack.sh  # X libs, GLib/GI, GTK2/3
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
./scripts/assemble_desktop_repo.sh        # base + non-base RPMs -> build/repo-desktop
SUBDIR=desktop REPO=build/repo-desktop META=xfce-desktop \
    ./scripts/publish_repo.sh             # -> packages/13.1/desktop/
./scripts/qemu_boot_graphical.sh          # desktop rootfs + X session + xwd capture
```

### Boot the rootfs under QEMU

```bash
cd ~/browneye
./bbuild build linux                  # once, ~5-10 min
./scripts/qemu_boot.sh                # installs kernel + modules, boots
```

`qemu_boot.sh` does:

1. copies `linux-kernel`/`linux-modules` into `build/repo`;
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
Kernel 7.1.8 on an x86_64 (ttyS0)
localhost login:
```

`timeout 180` kills QEMU on purpose (exit 124). Check
`grep -a FAILED build/qemu-boot.log`; it should be empty.

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
12. **Kernel headers are a bootstrap package.** `linux-api-headers` is built
    by copying the host's `kernel-headers` 7.2.4 UAPI directories
    (`linux/`, `asm/`, `asm-generic/`, `drm/`, …). It is required to compile
    anything that includes `<limits.h>`/`<linux/limits.h>`. Phase 2 should
    replace it with headers generated from the pinned kernel source via
    `make headers_install`. Do not treat it as a reproducible LFS package.
13. **`rpm` owns `/rpmbuild` by default.** The container writes build trees
    under `/rpmbuild` (not `/build`). Mount sources read-only and copy RPMs
    out, or change `%_topdir` in `browneye-rpm-config` deliberately.

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
      `/usr/bin` there, and that is reflected in `%files`.  Booting through
      grub and installing it to a disk are still untested.

### C. Remaining base hardening before phase-2 boot

- [x] C1. `glibc-locales` subpackage: `make localedata/install-locales`
      installs the full `localedata/SUPPORTED` set as a single
      `/usr/lib/locale/locale-archive` (223 MB, 886 locales).  It builds
      offline in the container, is required by `browneye-base`, and the
      installed rootfs reports 888 entries from `locale -a`;
      `de_DE.UTF-8` and `ja_JP.UTF-8` were checked at runtime.
- [x] C2. QEMU boot test: kernel 7.1.8 + ext4 rootfs boots to multi-user and
      a serial login prompt. `scripts/qemu_boot.sh` is the reproducible path.
      Re-verified for `build/rootfs-selfhost` on 2026-10-31 after C1/C3.
      No initramfs or bootloader yet.
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
      `ttyS0` was tested (`LOGIN_OK`, `uid=0`, kernel 7.1.8). Root is locked
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
- [x] C6c. Non-base stack synced to BLFS r13.1 and rebuilt offline in a
      persistent container (see `scripts/build_blfs_stack.sh`): X libraries
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
- [ ] C7. Revisit duplicate/disabled specs: `browneye-basefs-nousr.spec.disabled`,
      `browneye-init.spec.disabled`, `sysvinit.spec.disabled`, `yum.disabled`.
- [x] C8. Two-phase order documented: `package_specs/ORDER` stays
      chapter-8 + bootstrap extras, and `scripts/verify_base_in_container.sh`
      appends `libbsd`, `libmd`, `libseccomp`, and `browneye-base` for the
      full 93-package run.
- [ ] C9. Replace the host-derived `linux-api-headers` with
      `make headers_install` from the pinned kernel source (7.1.8).
- [ ] C10. Add an initramfs (dracut in the target or a custom cpio) and a
      bootloader path; the current QEMU boot relies on built-in virtio/ext4
      and `-kernel`. E3 covers a grub disk boot, E4 the generator/config.
- [x] C11. Close the self-hosting gaps found by rebuilding the base inside the
      container: rebuild texinfo/tcl before their users, bootstrap pip, and
      install the new RPMs into a fresh rootfs/image.  The fresh image rebuilt
      all 93 packages offline in the second-generation run.

### D. Phase 2 (D3 done; D2 remains out of current scope)

- [x] D1. Kernel packaging: `linux-kernel`/`linux-modules` 7.1.8 with the
      QEMU config. These RPMs are still host-built; rebuilding them inside
      the self-hosted image is tracked as E2.
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
      21.1.24 (meson; `-Dglamor=true -Dglx=false -Dsuid_wrapper=true
      -Dsystemd_logind=false`), X libraries (`libxcvt` 0.1.3, `libtirpc`
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
- [x] D5. **Desktop repository published.**  `scripts/assemble_desktop_repo.sh`
      collects the base repo plus every BLFS/XFCE/desktop RPM into
      `build/repo-desktop` (215 RPMs).  `scripts/publish_repo.sh` gained
      `SUBDIR`/`META` support; the desktop repo is
      `https://tomfool.8bit.ca/browneye/packages/13.1/desktop/` with
      `browneye-13.1-desktop.repo` and the `xfce-desktop` meta.  The landing
      page links it.

### E. Self-hosting and boot follow-ups (open)

These are the current caveats that do not yet have a checkbox elsewhere.

- [ ] E1. Build `dnf`/`libdnf` + `createrepo_c` (and their dependency stack)
      and move repo/rootfs assembly into the self-hosted image. Today
      `scripts/bootstrap_selfhosted.sh` still calls host `dnf`/`createrepo_c`
      (see A3/A4 and §7).
- [ ] E2. Rebuild `linux-kernel` and `linux-modules` 7.1.8 inside the
      self-hosted container and add them to the self-hosted repo. The current
      kernel RPMs were built on the host and are not part of the 93-package
      base set used for the second-generation proof.
- [ ] E3. Install grub to a disk image and boot without QEMU `-kernel`.
      grub builds and packages now, but only the direct-kernel QEMU path has
      been tested; C10 still covers the initramfs/bootloader-policy work.
- [ ] E4. Replace the QEMU-test kernel config with a general-purpose config,
      and add firmware, module signing, and initramfs generation. The current
      config has virtio/ext4/serial built in and no firmware/signing.
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
- GTK2's BLFS consolidated-fixes patch is no longer published; it builds
  with GCC 16 diagnostic relaxations (`-Wno-error=incompatible-pointer-types`,
  `-Wno-error=implicit-int`, ...) instead.
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
- The repo is unsigned and can contain several versions of the same package.
- Rootfs installs use `--setopt=tsflags=noscripts`; scriptlet correctness has
  not been tested outside the fake-root install.
- The container image is rootless/local (`localhost/browneye/base:...`) and
  not pushed anywhere.
- `package_specs/browneye-release` currently owns `/etc/os-release` as a
  symlink into `/usr/lib`; verify package ownership if you change it.
- `linux-api-headers` is copied from the **host's** `kernel-headers` 7.2.4,
  not built from kernel source. It is a bootstrap-only package; replace it
  with `make headers_install` from the pinned 7.1.8 kernel (C9).
- The RPM toolchain (`rpm`, `libarchive`, `lua`, `popt`) was initially built
  against host devel prefixes (`build/deps/*`), but the second-generation
  rebuild compiled it inside the self-hosted image. Ch5–7 bootstrap is still
  absent; the container relies on the chapter-8 toolchain.
- The container has no `dnf`/`createrepo_c`; host tools are required to
  assemble a new rootfs or refresh the repo. The **build** is self-hosted;
  the **assembly** is still host-assisted.
- `build/repo` is not pruned: 111 RPMs include old versions, debuginfo from
  early builds, and both `sqlite` and the retired `sqlite3` name.
- The kernel RPMs (`linux-kernel`, `linux-modules`) are **host-built** and are
  not part of the 93-package base set; E2 tracks rebuilding them inside the
  self-hosted container.
- The kernel config is derived from the old 6.4.12 LFS config plus hand-picked
  virtio/ext4/serial options. It is a QEMU-test config, not a general-purpose
  distro config. No initramfs, no firmware, no module signing (E4).
- The kernel spec copies `arch/x86/boot/bzImage` directly instead of using
  `make install`; the latter tried to write a systemd-boot entry to the host
  `/boot/efi` during rpmbuild.
- `scripts/qemu_boot.sh` uses `unshare -r` for `mke2fs -d` because
  `/etc/shadow` and `/etc/gshadow` are mode 000.
- The QEMU login test used a temporary SHA-512 root password, then restored
  the locked shadow entry. There is no first-boot password setup or account
  policy yet.
- **No Mesa:** there is no `libGL`/GLX.  `xorg-server` is built with
  `-Dglx=false` and logs "No glamor support in the X Server"; `xfwm4`
  compositing is disabled in the test session, and `xf86-video-amdgpu`
  cannot build (it needs `gbm`).  The `modesetting` DDX is used for KMS
  hardware; `xf86-video-vesa` is the fallback.
- **No SVG loader:** `gdk-pixbuf` is built with `glycin` disabled and
  `librsvg` is absent, so SVG icons/wallpapers do not render.  The hicolor
  PNG icons from XFCE work (`hicolor-icon-theme` is required by the meta).
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

## 8. Suggested first three actions for the new agent

1. **Build Mesa, then re-enable compositing.** Mesa provides `libGL`/GLX
   and `gbm`; without it Xorg records "No glamor support", xfwm4 cannot
   composite, and `xf86-video-amdgpu` cannot build.  Then rebuild
   `xorg-server` with `-Dglx=true`, test the xfwm4 compositor, and add
   `librsvg` or `glycin` for SVG icons/wallpapers.  A display manager
   (`lightdm`) needs Linux-PAM and a PAM-enabled systemd rebuild; `startx`
   is the current session entry point.
   After that, **add an initramfs and bootloader path** (dracut or a custom
   cpio, grub disk boot) for hardware and module-based storage.
2. **Replace the host-derived `linux-api-headers`** with
   `make headers_install` from the pinned 7.1.8 source, then rebuild the
   packages that consume UAPI headers.
3. **Decide whether rootfs assembly must also be self-hosted.** The build is
   now self-hosted; `dnf` + `createrepo_c` are still host tools. Build them
   only if the assembly pipeline itself must run in the container.

---

## 9. Useful one-liners

```bash
# what base packages are still missing from the repo?
python3 - <<'PY'
import json, glob, os, subprocess
lock=json.load(open('lfs.lock')); names=set()
for p in glob.glob(os.path.expanduser('~/rpmbuild/RPMS/x86_64/*.rpm')):
    if 'debug' in os.path.basename(p): continue
    try: names.add(subprocess.check_output(['rpm','-qp','--qf','%{NAME}',p],text=True))
    except Exception: pass
def present(n):
    c=lock['canonical_names'].get(n,n); s=lock['aliases'].get(n,n)
    return c in names or s in names or n in names
print([n for n in lock['base_packages'] if not present(n)])
PY

# inspect base meta requirements
rpm -qpR ~/rpmbuild/RPMS/x86_64/browneye-base-13.1-1.x86_64.rpm | sort

# find host-contaminated requires across the repo
for r in build/repo/*.rpm; do rpm -qpR "$r" 2>/dev/null | grep -qE 'libselinux|libxml2|libwayland|libxkbcommon|libcrypto\.so\.3|libssl\.so\.3' && basename "$r"; done
```
