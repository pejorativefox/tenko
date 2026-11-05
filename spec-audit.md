# Browneye spec audit — LFS/BLFS trunk

Audit of `package_specs/` against the LFS and BLFS checkouts and the
**published** repository, 2026-11-05.

- Repo snapshot: `repodata/22a5418…-primary.xml.zst` of
  <https://tomfool.8bit.ca/browneye/packages/13.1/> —
  **669 RPM names** from **477 source packages**.
- Books: `~/repos/lfs` branch `trunk` (`1493db7`) and `~/repos/blfs`
  branch `trunk` (`60fb6e5`).
- Spec tree after the two 2026-11-05 package waves (the 11-package
  version sync and the 21-package library/desktop wave), the Python 2 /
  Docker removals and the `lua-lgi` → `lgi` consolidation.
- Regenerate with `python3 scripts/spec_audit.py --primary primary.xml.zst`
  (see §5).

Book versions are read from every `*-version` entity in the two books
(all BLFS `*.ent` chapter files included), LFS first so a name collision
resolves to the LFS chapter-8 version (`xml-parser` is 2.57 in LFS, 2.59
as a BLFS perl module). Known renames are aliased (`gtkmm`→`gtkmm3`,
`gtk+`→`gtk3`, `webp`→`libwebp`, `libopus`→`opus`,
`libpoppler`→`poppler`, `libx264`→`x264`, `libx265`→`x265`,
`openjpeg`→`openjpeg2`, …). A package whose book page hard-codes its
version instead of using an entity — `htop`, `gstreamer`, `vte`,
`libyaml`, several binary bundles — cannot be compared this way and is
reported as **NO-BOOK** ("not comparable"), not as "not in the books".

## Executive summary

| measure | count |
|---|---:|
| spec files / spec directories | 507 / 505 |
| shipped spec files (live source package in the repo) | 477 |
| source packages in the published repo | 477 |
| RPM names in the published repo | 669 |
| **shipped packages below the book** | **0** |
| shipped packages at the book | 380 |
| shipped packages above the book | 1 (`xml-parser`, approved) |
| shipped packages with no comparable book entity | 96 |
| unbuilt spec files | 30 |
| unbuilt specs below the book | 0 |
| unbuilt specs at the book | 3 |
| unbuilt specs above the book | 1 (`db`) |
| unbuilt specs with no comparable book entity | 26 |
| specs with `Summary: TODO` | 59 |
| specs with `TODO` in `%description` | 73 |
| shipped specs with a missing referenced patch | 0 |
| shipped specs with a sources/version mismatch | 0 (9 audit false positives, §1.3) |
| specs with neither `sources` nor `nosources` | 0 |

**Bottom line.** Version parity for everything the distro ships still
holds: no shipped package is below LFS/BLFS trunk, and the only shipped
package above it (`xml-parser` 2.59 vs 2.57) is allowed by the "at least
the book version" rule. The unbuilt remainder is now 34 specs, none of
them below the book.

## 1. Shipped packages

380 shipped source packages match the book exactly and one
(`xml-parser`) is newer. The 96 without a comparable entity fall into
five groups; the version-bearing packages added on 2026-11-05 were
checked against upstream (see §1.2):

- **Distro-specific metas and config** (13): the `browneye-*` packages
  (`base`, `base-build`, `base-runtime`, `basefs`, `build`,
  `desktop-config`, `firstboot`, `installer`, `live`, `release`,
  `rpm-config`, `sysconfig`, `workstation`).
- **RPM/dnf stack not covered by the books** (11): `rpm`, `dnf`,
  `libdnf`, `libsolv`, `librepo`, `libcomps`, `libmodulemd`,
  `createrepo_c`, `zchunk`, `libostree`, `flatpak`.
- **Binary bundles** (8): `firefox-bin`, `google-chrome-bin`,
  `kitty-bin`, `opencode-bin`, `podman-bin`, `herdr`, `passt`, `tea`.
- **Fonts** (5): `font-siji`, `font-terminus`, `font-ttf-unifont`,
  `font-ubuntu-font-family`, `liberation-fonts`.
- **Book pages that hard-code their version or use another page name**
  (14): `htop` 3.5.3, `gstreamer`/`gst-plugins-base` 1.28.8,
  `vte` 0.84.1, `libyaml` 0.2.5, `libsecret` 0.21.8.2,
  `squashfs-tools` 4.7.5, `mtools` 4.0.50, `privoxy` 4.2.0,
  `dracut` 112, `cairomm` 1.14.6, `glib` 2.90.1, the four
  `xfce-desktop*` metas.
- **Other book-less packages** (45): `bash-completion`, `bwm-ng`,
  `docbook-xml`, `docbook-xsl-nons`, `libbsd`, `libcap-ng`, `libmd`,
  `linux-api-headers`, `linux-firmware`, `openvpn`, `proxychains-ng`,
  `pulsemixer`, `pyenv`, `python-flit-core`, `python-jinja`,
  `python-markupsafe`, `python-packaging`, `python-pyparsing`,
  `python-wheel`, `python3-docutils`, `python3-lxml`,
  `python3-pyelftools`, `rofi`, `tmux`, `xbacklight`, `xcb-util-xrm`,
  `xf86-input-libinput`, the five `xf86-video-*` drivers, and the 13
  packages added by the second wave (`acpi`, `awesome`, `bspwm`,
  `dunst`, `dwm`, `lgi`, `libstemmer`, `libxdg-basedir`, `ncdu`,
  `sdl2-image`, `sdl2-ttf`, `sxhkd`, `wmname`).

Known deviations and exceptions are recorded in issue #7.

### 1.1 Source metadata corrected in the 2026-11-03 pass

The audit checks each `sources` file against the spec `Version`. Seven
shipped specs carried stale source names and were fixed then (the URL was
already correct in most cases; the local filename was not):

| package | problem | fix |
|---|---|---|
| `brotli` | URL 1.2.1, local name `brotli-1.2.0.tar.gz` | name 1.2.1 |
| `c-ares` | URL 1.34.9, local name 1.34.8 | name 1.34.9 |
| `libpng` | URL 1.6.59, local name 1.6.58 | name 1.6.59 |
| `nmap` | URL 7.993, local name 7.991 | name 7.993 |
| `simdutf` | URL 9.3.3, local name 9.2.1 | name 9.3.3 |
| `xorgproto` | URL 2026.1, local name 2025.1 | name 2026.1 |
| `xorg-server` | URL fetched 21.1.24 while the spec says 21.1.25 | URL + md5 21.1.25 |

`glib`'s bootstrap stage (`glib-pass1`) was deleted at the same time,
together with the scratch-bootstrap scripts. The published repo is the
checkpoint: package-level rebuilds run in a base image built from it, and
the stack build now expects `glib` in that image.

### 1.2 Package waves published 2026-11-05

**First wave, 11 packages** (book versions where the r13.1 books have a
page; the rest approved latest-stable deviations, issue #7):

| package | version | basis |
|---|---|---|
| `gtkmm` | 3.24.11 | BLFS r13.1 (page `gtkmm3`) |
| `libpeas` | 1.38.1 | BLFS r13.1 |
| `webp` (libwebp) | 1.6.0 | BLFS r13.1 |
| `tmux` | 3.8 | latest upstream stable, no book page |
| `openvpn` | 2.7.8 | latest upstream stable, no book page |
| `rofi` | 2.0.0 | latest upstream stable, no book page |
| `xf86-video-fbdev` | 0.5.1 | latest upstream stable, archive-only |
| `xf86-video-intel` | 20230223 | newest snapshot, archive-only |
| `xf86-video-vmware` | 13.4.0 | latest release, archive-only |
| `xbacklight` | 1.2.4 | latest upstream stable, no book page |
| `libcap-ng` | 0.9.6 | new dependency of OpenVPN 2.7.8, no book page |

**Second wave, 21 packages** (codec/PDF, desktop and utility set):

| package | version | basis |
|---|---|---|
| `openjpeg` | 2.5.4 | BLFS r13.1 `general/graphlib/openjpeg2.xml` |
| `libtheora` | 1.1.1 | BLFS book version (page is archive-only; still latest) |
| `libopus` | 1.6.1 | BLFS r13.1 `multimedia/libdriv/opus.xml` |
| `libstemmer` | 3.2.0 | no book page; latest upstream stable |
| `libx264` | 20250815 | BLFS r13.1 `multimedia/libdriv/x264.xml` |
| `libx265` | 4.3 | BLFS r13.1 `multimedia/libdriv/x265.xml` |
| `libpoppler` | 26.10.0 | BLFS r13.1 `general/graphlib/poppler.xml` |
| `dconf` | 51.0 | BLFS r13.1 `gnome/platform/dconf.xml` |
| `libxdg-basedir` | 1.2.3 | no book page; latest upstream tag |
| `dunst` | 1.13.2 | no book page; latest upstream stable |
| `lgi` | 0.9.2 | no book page; latest upstream tag, Lua 5.4/GLib 2.86 patches |
| `awesome` | 4.3 | no book page; latest tagged release |
| `bspwm` | 0.9.12 | no book page; latest upstream tag |
| `sxhkd` | 0.6.3 | no book page; latest upstream tag |
| `dwm` | 6.5 | no book page; latest upstream stable |
| `wmname` | 0.1 | no book page; latest upstream stable |
| `yasm` | 1.3.0 | BLFS r13.1 `general/prog/yasm.xml` |
| `acpi` | 1.8 | no book page; latest upstream stable (2025) |
| `ncdu` | 1.22 | no book page; latest C-series (2.x requires Zig) |
| `sdl2-image` | 2.8.12 | no book page; latest SDL2-series release |
| `sdl2-ttf` | 2.24.0 | no book page; latest SDL2-series release |

All 32 wave RPMs were verified on both the public site and the LAN
mirror, and the 21 second-wave packages install together into a clean
dnf installroot (102 packages).

### 1.3 Sources/version mismatches that remain

The nine rows the script prints are all expected:

- Date/commit-named archives: `font-siji`, `passt`.
- Binary bundles: `herdr`, `opencode-bin`, `podman-bin`.
- SF "download" aliases: `font-terminus`.
- `sqlite`: the book/spec version 3.54.1 is the autoconf number 3540100.
- `autoconf213`: the shared `sources` file lists the 2.73 tarball first;
  the 2.13 patch 404s upstream (issue #8).
- `fuse`: shared-directory layout. `fuse/sources` lists `fuse-2.9.7`
  (for `fuse2`) before `fuse-3.2.5`.

### 1.4 Open shipped-package debt

- **`Summary: TODO` / `TODO` descriptions** in 59 and 73 specs — issue #8.
- **Images lag the repo**: the published installer ISO and rootfs were
  built before both 2026-11-05 waves and do not contain them. They are
  only rebuilt on request (AGENTS.md).
- **`imagemagick` 7.1.2-2 has no PNG coder** (`convert` reports "no
  decode delegate … png"). Found while deriving a desktop build image;
  the spec/RPM were not changed. Needs a fix before the next image
  rebuild (issue #8).

## 2. Unbuilt specs (30)

30 spec files have no matching source package in the published repo: 26
have no comparable book entity, 3 are at the book, 1 is above it (`db`
6.2.32 vs 5.3.28), and none is below it.

They cost nothing while they stay unbuilt, but the parity rule in
`AGENTS.md` applies the moment someone builds one. Grouped by intent:

| group | count | examples |
|---|---:|---|
| Media / system libraries | 10 | `libsoup`, `pcre`, `fuse`, `db`, `cppunit` |
| Container / k8s / packaging | 6 | `kubectl`, `kubectx`, `drpm`, `rpmlint` |
| CLI / dev tools | 6 | `cdrkit`, `go-bin`, `gotop`, `help2man` |
| Boot / init | 3 | `syslinux`, `pm-utils`, `tzdb` |
| X11 tools | 4 | `x11perf`, `libdmx`, `xf86-input-synaptics` |
| Fonts | 1 | `woff2` |

The three unbuilt specs at the book version are `autoconf213` (2.13),
`pm-utils` (1.4.1) and `woff2` (1.0.2). `db` 6.2.32 is above the book's
5.3.28, which the parity rule allows.

A handful of names in this bucket may be mismatches rather than truly
unbuilt; check before deleting anything.

### 2.1 Py2/Python3/Docker/other retirements

Ten specs whose BLFS pages live only in `book/archive/` and which had no
RPM in the repository were deleted in the 2026-11-03 pass: `atk`,
`at-spi2-atk`, `check`, `dhcp`, `gtk-xfce-engine`, `libcroco`, `mandoc`,
`python2`, `udev`, `xfce4-xkb-plugin`.

The 2026-11-05 Python 2 cleanup retired the remaining six `python2-*`
packages (`pip`, `psutil`, `pycairo`, `pycurl`, `pygobject`,
`setuptools`) and the Python 2-only `terminator` 1.91 spec. The distro
ships no Python 2 interpreter, so none of them could be built.

The 2026-11-05 container cleanup retired the `docker` 18.06.3 and
`docker-compose` 1.27.0-rc1 specs. The distro uses podman; the `dive`
spec stays because it inspects OCI images and does not need the Docker
daemon.

The 2026-11-05 Python 3 cleanup retired 29 unbuilt specs: the Sphinx
documentation stack (`python-sphinx` plus 18 dependencies) and ten
standalone modules (`pip`, `six`, `mako`, `distro`, `scikit-build`,
`pycairo`, `pygobject`, `pygpgme`, `importlib_metadata`, `zipp`).
Nothing shipped required any of them, `pip` is already provided by
ensurepip in the Python package, and the Sphinx stack only served
`dnf-plugins-core`'s man pages — that spec now builds without it.

A second 2026-11-05 cleanup retired 19 more unused specs: `polybar`,
`font-noto-cjk`, `busybox`, `eudev`, `finit`, `kdevelop-bin`,
`dnf-plugins-core`, `dive`, the seven Perl modules (`perl-cgi`,
`perl-crypt-password-md5`, `perl-dbi`, `perl-digest-sha1`,
`perl-io-sockets-ssl`, `perl-ssleay`, `perl-uri`), `transgui-bin`, and
the SDL1 trio (`sdl`, `sdl-image`, `sdl-ttf`). None was shipped, and no
remaining spec required any of them. Dropping the Perl modules means
`syslinux` would need them recreated before it can be packaged.

The second wave replaced the old `lua-lgi` spec directory with
`package_specs/lgi` (same `Name`/version, plus the Lua 5.4 and
GLib 2.86+ fixes), so `lua-lgi` was removed instead of leaving two specs
for one package.

### 2.2 Deliberately skipped

- **SDL1**: the `sdl`/`sdl-image`/`sdl-ttf` specs were retired on
  2026-11-05. SDL2 2.32.74 and SDL3 3.4.18 are shipped at the book
  versions, and `sdl2-image`/`sdl2-ttf` are shipped from the second
  wave.
- **`syslinux`**: builds as 6.04-pre1 with a modern-toolchain patch, but
  `sha1pass`/`md5pass` require `perl(Crypt::PasswdMD5)` and
  `perl(Digest::SHA1)`, neither in LFS/BLFS. Not published; work is kept
  on branch `pkg-syslinux` (`1a67ba5`). Those two module specs were also
  dropped in the 2026-11-05 cleanup, so completing `syslinux` would mean
  recreating them.
- **`autoconf213`**: unbuildable — its consolidated-fixes patch 404s and
  is not vendored (issue #8).

## 3. Newer or older than the book

| package | local | book | status |
|---|---|---|---|
| `xml-parser` | 2.59 | 2.57 | shipped; allowed ("at least the book") |
| `db` | 6.2.32 | 5.3.28 | unbuilt stub; allowed |

`sqlite` 3.54.1 is **not** newer: the book entity `sqlite-version` is the
autoconf build number `3540100`, which equals 3.54.1. The script converts
it; other tools report it as a false mismatch.

## 4. What this audit did not cover

- Cross-compilation and non-x86_64: the repo is x86_64 only.
- Optional BLFS features with no spec (Wayland, PipeWire, printing, …);
  those are product decisions rather than version skew.
- The 26 unbuilt no-entity specs are not individually version-checked;
  `scripts/spec_audit.py` prints the list and compares whatever the books
  expose as entities.

## 5. Reproduction

```sh
# 1. latest published repodata
curl -s https://tomfool.8bit.ca/browneye/packages/13.1/repodata/repomd.xml \
  | grep -o '[a-f0-9]*-primary.xml.zst' | head -1
curl -sO https://tomfool.8bit.ca/browneye/packages/13.1/repodata/<hash>-primary.xml.zst

# 2. the audit (needs ~/repos/lfs and ~/repos/blfs, zstd, python3)
python3 scripts/spec_audit.py --primary <hash>-primary.xml.zst
```

`scripts/audit_versions.py --primary <file>` still works for a flat
RPM-name list; it counts subpackages as separate rows.
