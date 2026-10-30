# Handoff — browneye LFS r13.1 base rebuild

Last updated: 2026-10-30. Branch: `lfs-r13.1`. Work root: `~/browneye`.

Read this first. It supersedes the earlier wave-by-wave plan; the history is in
`git log` and the old text is no longer the source of truth.

---

## 1. TL;DR

**Item 1 (LFS version parity) is effectively complete for the base system.**

- 79 of 80 chapter-8 packages build from specs. Only **grub** is deferred.
- Local repo: `build/repo`, 111 RPMs (includes old versions/debuginfo; clean before publish).
- `browneye-base` meta resolves and installs 93 packages into `build/rootfs`.
- Rootfs verified inside a chroot: bash 5.3, python 3.14.7, openssl 4.0.1,
  merged `/usr` layout, loader at `/usr/lib64/ld-linux-x86-64.so.2`.

**Item 2 (build container) now has a working RPM toolchain.**

- Image `localhost/browneye/base:r13.1-rpm5-20261030` exists (1.3 GB).
- Contains `rpm` 4.18.1 + `rpmbuild`, `browneye-rpm-config`, and the base
  toolchain. `rpm -qa` sees all 93 installed packages (sqlite rpmdb at
  `/usr/lib/sysimage/rpm`).
- Verified inside the container: build a C package with `rpmbuild -bb`,
  install it with `rpm -Uvh`, run it, remove it; and build `which-2.21`
  directly from `package_specs/`.
- `dnf` and `createrepo_c` are **not** in the image yet. Decision: keep repo
  assembly and rootfs installs on the host for now (§6 A3/A4).

**Phase 2 boot smoke test is green (2026-10-30).**

- Kernel **7.1.8** built with virtio-blk/virtio-pci/serial/ext4 built in;
  packages are `linux-kernel` and `linux-modules`.
- `scripts/qemu_boot.sh` installs the kernel into the rootfs, materializes
  sysusers, builds a raw ext4 image, and boots it under QEMU/KVM.
- Boot log: no `FAILED` units, `Reached target Multi-User System`, serial
  `login:` prompt, `Browneye Linux 13.1 / Kernel 7.1.8`.
- This is still a serial-console/login test; no bootloader, initramfs, or
  root password policy yet.

---

## 2. Environment and layout

- Host: Fedora 44, x86_64, 16 cores / 32 GB, podman 5.8, dnf5, rpm 6.0.2,
  host gcc 16.2.1 / binutils 2.46.1. `sudo` requires a password; use
  `unshare -r` for anything needing fake root (see §5).
- Main checkout: `~/repos/browneye` on `master` (contains the merged
  `gcc-13-update` history).
- Work root: `~/browneye`, a git worktree on branch `lfs-r13.1`.
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
│   └── sync_lfs_spec.py       # dry-run/--write version+source sync
├── lfs.lock                   # pinned versions/sources/patches/base list
├── Containerfile              # FROM scratch + rootfs tarball
└── build/
    ├── repo/                  # createrepo_c output (105 rpms, some stale)
    ├── rootfs/                # installed base system (1.3 GB)
    ├── browneye-rootfs.tar.gz # 374 MB, built under unshare -r
    └── deps/                  # extracted devel prefixes (see §5)
```

---

## 3. Decisions (still in force)

| # | Decision | Value |
|---|---|---|
| D1 | Init | **systemd 261.2** (book systemd variant) |
| D2 | Library layout | **`/usr/lib64`**, merged `/usr` via basefs symlinks |
| D3 | Kernel | **deferred to phase 2** |
| D4 | Bootstrap | **chapter 8 built with host toolchain** (ch5–7 deferred) |
| D5 | LFS pin | **r13.1 tag** (`71ef60ba`) |

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

### Boot the rootfs under QEMU

```bash
cd ~/browneye
./bbuild build linux                  # once, ~5-10 min
./scripts/qemu_boot.sh                # installs kernel + modules, boots
```

`qemu_boot.sh` does:

1. copies `linux-kernel`/`linux-modules` into `build/repo`;
2. `dnf --installroot build/rootfs install linux-kernel linux-modules`;
3. runs `systemd-sysusers` inside the rootfs (install scriptlets were skipped);
4. writes a machine-id and runs `depmod -b`;
5. `mke2fs -d build/rootfs` → `build/rootfs.img` (3 GB);
6. boots with `root=/dev/vda console=ttyS0` and logs to `build/qemu-boot.log`.

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

- [ ] B1. `grub 2.14`. Current state: after disabling LTO and hardened flags
      it fails at configure with "cannot run C compiled programs" due to
      `--target=x86_64` cross detection. Options: build in a Fedora 39/40
      container (matches LFS era), add a proper `--host`/`--build` pair, or
      defer until the kernel/boot phase. It is **not needed** for the runtime
      base.

### C. Remaining base hardening before phase-2 boot

- [ ] C1. glibc locales (`glibc-locales` subpackage) — currently skipped.
- [x] C2. QEMU boot test: kernel 7.1.8 + ext4 rootfs boots to multi-user and
      a serial login prompt. `scripts/qemu_boot.sh` is the reproducible path.
      No initramfs or bootloader yet.
- [ ] C3. systemd chapter-9 config: unit presets/enablement, journald/networkd
      defaults, udev rules, `/etc/systemd/*`. Current state: `default.target`
      and `serial-getty@ttyS0` are symlinked by `browneye-sysconfig`, and
      `qemu_boot.sh` runs `systemd-sysusers` before imaging. Presets and
      network/journal configuration are still bare.
- [ ] C4. `/etc/passwd`/`group`/`shadow` baseline: root and system users now
      exist through `systemd-sysusers`, but there is no root password policy
      and no login test beyond the `agetty` prompt.
- [ ] C5. Clean `build/repo` of stale/duplicate/debuginfo RPMs, regenerate.
- [ ] C6. Tighten broad `%files` back to filelists/globs per package; regenerate
      the remaining static filelists (`glib`, `gobject-introspection`, `groff`,
      `gtk2`, `gtk3`, `imagemagick`, `kbd`, `llvm`, `tcl`).
- [ ] C7. Revisit duplicate/disabled specs: `browneye-basefs-nousr.spec.disabled`,
      `browneye-init.spec.disabled`, `sysvinit.spec.disabled`, `yum.disabled`.
- [ ] C8. `package_specs/ORDER` now includes the bootstrap extras
      (`linux-api-headers`, `popt`, `libarchive`, `lua`, `rpm`,
      `browneye-rpm-config`) but still not `libbsd`, `libmd`, `libseccomp`,
      or `browneye-base`; extend it or document the two-phase order.
- [ ] C9. Replace the host-derived `linux-api-headers` with
      `make headers_install` from the pinned kernel source (7.1.8).
- [ ] C10. Add an initramfs (dracut in the target or a custom cpio) and a
      bootloader path; the current QEMU boot relies on built-in virtio/ext4
      and `-kernel`.

### D. Phase 2 (explicitly out of current scope)

- [ ] D1. Kernel packaging (linux 7.1.8 from the tag) + `.config`.
- [ ] D2. Chapters 5–7 self-hosted toolchain as bootstrap RPMs.
- [ ] D3. X/Wayland/desktop stack, BLFS packages.

---

## 7. Known technical debt

- Base packages were built against the **host** (Fedora 44) compiler and
  libraries. We removed the obvious leaks, but any new build can reintroduce
  a host-only `DT_NEEDED`. Always test dependency closure by reinstalling the
  rootfs after adding packages.
- Many `%files` sections are directory globs. This hides file ownership bugs
  and makes upgrades noisy.
- `browneye-base` has 92 `Requires:` (generated from `lfs.lock` plus the
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
  with `make headers_install` from the pinned kernel in phase 2.
- `rpm`, `libarchive`, `lua`, and `popt` were built against host devel
  prefixes (`build/deps/*`) and/or host toolchain. They are in-repo, but the
  RPM toolchain is not yet self-hosted (no ch5–7 bootstrap).
- The container has no `dnf`/`createrepo_c`; host tools are required to
  assemble a new rootfs or refresh the repo.
- `build/repo` is not pruned: 111 RPMs include old versions, debuginfo from
  early builds, and both `sqlite` and the retired `sqlite3` name.
- The kernel config is derived from the old 6.4.12 LFS config plus hand-picked
  virtio/ext4/serial options. It is a QEMU-test config, not a general-purpose
  distro config. No initramfs, no firmware, no module signing.
- The kernel spec copies `arch/x86/boot/bzImage` directly instead of using
  `make install`; the latter tried to write a systemd-boot entry to the host
  `/boot/efi` during rpmbuild.
- `scripts/qemu_boot.sh` uses `unshare -r` for `mke2fs -d` because
  `/etc/shadow` and `/etc/gshadow` are mode 000.
- The QEMU test does not log in; it only proves agetty/systemd reach a prompt.
  Root is locked and there is no password/login test yet.

---

## 8. Suggested first three actions for the new agent

1. **Make the boot test a real login test.** Set a root password (or add a
   test user), boot, log in over `ttyS0`, and run `systemctl status`,
   `journalctl`, `python3`, and `gcc` inside the VM.
2. **Add an initramfs and bootloader path.** The current QEMU boot depends on
   virtio/ext4/serial being built into the kernel. For real hardware and
   module-based storage, add dracut (or a custom cpio) and finish grub.
3. **Decide whether the build pipeline must be fully self-hosted.** Today
   rootfs assembly uses host dnf/createrepo; the container builds RPMs but
   cannot install a dependency graph. Building `dnf` + `createrepo_c` is a
   large dependency project; do it only if self-hosting is required.

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
