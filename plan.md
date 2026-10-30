# Handoff — browneye LFS r13.1 base rebuild

Last updated: 2026-10-30. Branch: `lfs-r13.1`. Work root: `~/browneye`.

Read this first. It supersedes the earlier wave-by-wave plan; the history is in
`git log` and the old text is no longer the source of truth.

---

## 1. TL;DR

**Item 1 (LFS version parity) is effectively complete for the base system.**

- 79 of 80 chapter-8 packages build from specs. Only **grub** is deferred.
- Local repo: `build/repo`, 105 RPMs.
- `browneye-base` meta resolves and installs 88 packages into `build/rootfs`.
- Rootfs verified inside a chroot: bash 5.3, python 3.14.7, openssl 4.0.1,
  merged `/usr` layout, loader at `/usr/lib64/ld-linux-x86-64.so.2`.

**Item 2 (build container) is partially complete.**

- Image `localhost/browneye/base:r13.1-20261030` exists (1.27 GB).
- Smoke-tested: bash, python3, openssl, and a gcc hello-world compile.
- The image does **not** yet contain `rpmbuild`, `dnf`, or `createrepo_c`, so it
  cannot build RPMs yet. That is the next task.

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

podman run --rm browneye/base:r13.1-20261030 /usr/bin/bash -lc \
  'bash --version | head -1; python3 -V; openssl version'
```

`tsflags=noscripts` is required because the install runs as a fake root and
package scriptlets (ldconfig, systemd sysusers, shadow) fail without real root.

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

---

## 6. What remains

### A. Item 2 bootstrap (highest priority)

- [ ] A1. Build `rpm` (spec exists at 4.18.1) and split/create `rpm-build`.
- [ ] A2. Add `rpm-build` + `rpm` to `browneye-base` and refresh the image.
- [ ] A3. Create a `createrepo_c` spec (missing) or provide repo tooling another way.
- [ ] A4. Build `dnf` (spec exists, 4.16.2) **or** decide to bind-mount the
      host's `dnf`/`rpmbuild` into the container for the outer build phase.
      dnf's dependency chain (`libdnf`, `libsolv`, python modules) is large;
      estimate before committing.
- [ ] A5. Create `browneye-rpm-config` (rpm macros + `strip_debug.sh`) so the
      container's `rpmbuild` does not depend on Fedora `brp-*` paths.
- [ ] A6. Verify inside the container:
      `rpmbuild -bb`, `rpm --eval '%_libdir'` = `/usr/lib64`, and build one
      non-base package (e.g. `glib`) from `package_specs/`.

### B. Close the last base package

- [ ] B1. `grub 2.14`. Current state: after disabling LTO and hardened flags
      it fails at configure with "cannot run C compiled programs" due to
      `--target=x86_64` cross detection. Options: build in a Fedora 39/40
      container (matches LFS era), add a proper `--host`/`--build` pair, or
      defer until the kernel/boot phase. It is **not needed** for the runtime
      base.

### C. Remaining base hardening before phase-2 boot

- [ ] C1. glibc locales (`glibc-locales` subpackage) — currently skipped.
- [ ] C2. QEMU boot test: the rootfs has not been booted. No kernel, initramfs,
      bootloader, machine-id, or `/etc/fstab` yet.
- [ ] C3. systemd chapter-9 config: unit presets/enablement, journald/networkd
      defaults, udev rules, `/etc/systemd/*`. `browneye-sysconfig` only has
      the bare `/etc` files.
- [ ] C4. `/etc/passwd`/`group`/`shadow` baseline: shadow ships tools, but no
      users are created. Add a base users/groups step.
- [ ] C5. Clean `build/repo` of stale/duplicate/debuginfo RPMs, regenerate.
- [ ] C6. Tighten broad `%files` back to filelists/globs per package; regenerate
      the remaining static filelists (`glib`, `gobject-introspection`, `groff`,
      `gtk2`, `gtk3`, `imagemagick`, `kbd`, `llvm`, `tcl`).
- [ ] C7. Revisit duplicate/disabled specs: `browneye-basefs-nousr.spec.disabled`,
      `browneye-init.spec.disabled`, `sysvinit.spec.disabled`, `yum.disabled`.
- [ ] C8. `package_specs/ORDER` does not include the bootstrap extras
      (`libbsd`, `libmd`, `libseccomp`, `libmd`) or `browneye-base`; extend it
      or document the two-phase order.

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
- `browneye-base` has 86 `Requires:` (generated from `lfs.lock`); it is not
  regenerated automatically when versions change.
- The repo is unsigned and can contain several versions of the same package.
- Rootfs installs use `--setopt=tsflags=noscripts`; scriptlet correctness has
  not been tested outside the fake-root install.
- The container image is rootless/local (`localhost/browneye/base:...`) and
  not pushed anywhere.
- `package_specs/browneye-release` currently owns `/etc/os-release` as a
  symlink into `/usr/lib`; verify package ownership if you change it.

---

## 8. Suggested first three actions for the new agent

1. **Make the container able to build RPMs:** add `rpm` + `rpm-build` +
   `browneye-rpm-config` to the base, rebuild repo/rootfs/image, and run
   `rpmbuild -bb` on a trivial spec inside the image.
2. **Decide the dnf path:** either build `dnf` 4.16.2 and its dependency chain,
   or bind-mount the host `dnf`/rpmbuild into the container and document it.
   Do not start the 400-package outer upgrade until this is settled.
3. **Boot the rootfs:** add kernel + initramfs + fstab/machine-id (phase 2
   entry), then boot in QEMU. This is the real acceptance test for Item 1.

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
