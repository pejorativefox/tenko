# Browneye spec audit — LFS/BLFS trunk

Audit of `package_specs/` against the LFS and BLFS checkouts and the
**published** repository, 2026-11-05.

- Repo snapshot: `repodata/870aadc…-primary.xml.zst` of
  <https://tomfool.8bit.ca/browneye/packages/13.1/> —
  **687 RPM names** from **495 source packages**.
- Books: `~/repos/lfs` branch `trunk` (`1493db7`) and `~/repos/blfs`
  branch `trunk` (`60fb6e5`).
- Spec tree after the three 2026-11-05 package waves, the Python 2/3 and
  Docker removals, and the `lua-lgi` → `lgi` consolidation.
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
| spec files / spec directories | 495 / 495 |
| shipped spec files (live source package in the repo) | 495 |
| source packages in the published repo | 495 |
| RPM names in the published repo | 688 |
| **shipped packages below the book** | **0** |
| shipped packages at the book | 382 |
| shipped packages above the book | 2 (`db`, `xml-parser`) |
| shipped packages with no comparable book entity | 111 |
| unbuilt spec files | 0 |
| unbuilt specs below the book | 0 |
| specs with `Summary: TODO` | 0 |
| specs with `TODO` in `%description` | 0 |
| shipped specs with a missing referenced patch | 0 |
| shipped specs with a sources/version mismatch | 0 (7 audit false positives, §1.3) |
| specs with neither `sources` nor `nosources` | 0 |

**Bottom line.** Version parity holds: no shipped package is below
LFS/BLFS trunk. The two packages above it (`db` 6.2.32 vs the archived
5.3.28 and `xml-parser` 2.59 vs 2.57) are allowed by the "at least the
book version" rule. Every spec in the tree now has a matching source
package in the published repository.

## 1. Shipped packages

382 shipped source packages match the book exactly and two are newer.
The 111 without a comparable entity fall into five groups; the
version-bearing packages added in the 2026-11-05 waves were checked
against upstream (§1.2):

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
- **Other book-less packages** (60): `bash-completion`, `bwm-ng`,
  `docbook-xml`, `docbook-xsl-nons`, `libbsd`, `libcap-ng`, `libmd`,
  `linux-api-headers`, `linux-firmware`, `openvpn`, `proxychains-ng`,
  `pulsemixer`, `pyenv`, the nine shipped `python-*`/`python3-*` helper
  modules, `rofi`, `tmux`, `xbacklight`, `xcb-util-xrm`,
  `xf86-input-libinput`, the five `xf86-video-*` drivers, plus the
  packages added by the second and third waves (`acpi`, `awesome`,
  `bspwm`, `cdrkit`, `drpm`, `dunst`, `dwm`, `fakeroot-ng`, `go-bin`,
  `gotop`, `help2man`, `lgi`, `libdmx`, `liblzo2`, `libsoup`,
  `libstemmer`, `libuev`, `libxdg-basedir`, `ncdu`, `numactl`, `pcre`,
  `sdl2-image`, `sdl2-ttf`, `sxhkd`, `tzdb`, `wmname`, `x11perf`,
  `xf86-input-synaptics`).

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

**Third wave, 18 packages** (the remaining system/tooling/X11 set):

| package | version | basis |
|---|---|---|
| `db` | 6.2.32 | above the archived book 5.3.28; current 6.x |
| `liblzo2` | 2.10 | BLFS r13.1 `general/genlib/lzo.xml` |
| `libsoup` | 2.74.3 | archived 2.x page (active book page is `libsoup3`) |
| `libuev` | 2.4.1 | no book page; latest upstream stable |
| `pcre` | 8.45 | archived PCRE1 page; final PCRE1 release |
| `woff2` | 1.0.2 | BLFS r13.1 `general/graphlib/woff2.xml` |
| `drpm` | 0.5.3 | no book page; latest upstream release |
| `fakeroot-ng` | 0.18 | no book page; latest upstream release |
| `cdrkit` | 1.1.11 | no book page; latest upstream release |
| `help2man` | 1.49.3 | no book page; latest GNU release |
| `numactl` | 2.0.19 | no book page; latest upstream release |
| `go-bin` | 1.27.3 | no book page; latest stable Go |
| `gotop` | 4.2.0 | no book page; latest maintained release |
| `pm-utils` | 1.4.1 | BLFS r13.1 `general/sysutils/pm-utils.xml` |
| `tzdb` | 2026f | book `tzdata` entity / current upstream; ships data only |
| `libdmx` | 1.1.5 | no book page; latest x.org release |
| `x11perf` | 1.6.1 | no book page; latest x.org release |
| `xf86-input-synaptics` | 1.10.0 | no book page; latest x.org release |

**Metadata and licence waves, 2026-11-05 (second pass).** PR #18 replaced
the `TODO` summaries and descriptions for 59 specs and verified their
licences (`curl` → `curl`, `cmake` → `BSD-3-Clause`, `libpng` →
`libpng-2.0`, `pcre2` → `BSD-3-Clause WITH PCRE2-exception`, `polkit` →
`LGPL-2.0-or-later`, `pulseaudio` → `LGPL-2.1-or-later`, …). PR #19 then
verified the remaining 118 specs that still said `License: GPL3` (`glib`
→ `LGPL-2.1-or-later`, `gcc` → `GPL-3.0-or-later WITH
GCC-exception-3.1`, `openssl` → `Apache-2.0`, `perl` → `Artistic-1.0-Perl
OR GPL-1.0-or-later`, `python` → `PSF-2.0`, `zlib` → `Zlib`, `ncurses` →
`X11`, `cairo` → `LGPL-2.1-only OR MPL-1.1`, …). All 177 packages were
rebuilt and published (80 + 207 RPMs including subpackages); the
repository now reports no `TODO` metadata and no `GPL3` placeholder.
`grub` now also ships `grub-mkfont` and `grub-mount`, which the rebuild
environment builds when freetype/fuse3 are present.

`mkfontdir` was retired rather than built: its only files are already
shipped by `mkfontscale` and the two packages conflict. `rpmlint` was
retired because its six Python runtime dependencies are not in the
books or the repo (§2.1).

All published RPMs were verified on both the public site and the LAN
mirror. The 18 third-wave packages install together into a clean dnf
installroot (79 packages total).

### 1.3 Sources/version mismatches that remain

The seven rows the script prints are all expected:

- Date/commit-named archives: `font-siji`, `passt`.
- Binary bundles: `herdr`, `opencode-bin`, `podman-bin`.
- SF "download" aliases: `font-terminus`.
- `sqlite`: the book/spec version 3.54.1 is the autoconf number 3540100.

### 1.4 Open shipped-package debt

- **Metadata and licences are clean.** PR #18 filled the 48 `Summary:
  TODO` and 11 description-only specs; PR #19 verified the last 118
  `License: GPL3` placeholders. Both waves were rebuilt and the repo now
  reports **0 TODO** summaries and **0 `GPL3`** licences.
- **`openssl-perl` has a dangling require**: `perl(Net::Curl::Easy)` is
  not provided by any package. The previous published RPM had the same
  require, so the rebuild does not regress it, but it needs a separate
  look.
- **Images lag the repo**: the published installer ISO and rootfs were
  built before all 2026-11-05 waves and do not contain them. They are
  only rebuilt on request (AGENTS.md).
- **`imagemagick` PNG support** — fixed in 7.1.2-3 (`54cc843`). The
  package had been built with `--with-modules`, so coders were loaded
  through libltdl; `brp-remove-la-files` strips the companion `.la`
  files, leaving no coder loadable. The coders are now built into
  `libMagickCore`.

## 2. Unbuilt specs (0)

None. Every spec in `package_specs/` now has a matching source package in
the published repository.

### 2.1 Py2/Python3/Docker/other retirements

Ten specs whose BLFS pages live only in `book/archive/` and which had no
RPM in the repository were deleted in the 2026-11-03 pass: `atk`,
`at-spi2-atk`, `check`, `dhcp`, `gtk-xfce-engine`, `libcroco`, `mandoc`,
`python2`, `udev`, `xfce4-xkb-plugin`.

The 2026-11-05 Python 2 cleanup retired the six `python2-*` packages
(`pip`, `psutil`, `pycairo`, `pycurl`, `pygobject`, `setuptools`) and
the Python 2-only `terminator` 1.91 spec. The distro ships no Python 2
interpreter, so none of them could be built.

The 2026-11-05 container cleanup retired the `docker` 18.06.3 and
`docker-compose` 1.27.0-rc1 specs. The distro uses podman; the `dive`
spec stayed until the second cleanup below removed it.

The 2026-11-05 Python 3 cleanup retired 29 unbuilt specs: the Sphinx
documentation stack (`python-sphinx` plus 18 dependencies) and ten
standalone modules (`pip`, `six`, `mako`, `distro`, `scikit-build`,
`pycairo`, `pygobject`, `pygpgme`, `importlib_metadata`, `zipp`).
Nothing shipped required any of them, `pip` is already provided by
ensurepip in the Python package, and the Sphinx stack only served
`dnf-plugins-core`'s man pages — that spec now builds without it.

A second cleanup retired 19 more unused specs: `polybar`,
`font-noto-cjk`, `busybox`, `eudev`, `finit`, `kdevelop-bin`,
`dnf-plugins-core`, `dive`, the seven Perl modules (`perl-cgi`,
`perl-crypt-password-md5`, `perl-dbi`, `perl-digest-sha1`,
`perl-io-sockets-ssl`, `perl-ssleay`, `perl-uri`), `transgui-bin`, and
the SDL1 trio (`sdl`, `sdl-image`, `sdl-ttf`).

A third cleanup retired `build-essential`, `autoconf213` (unbuildable
because its patch 404s), `kubectl`, `kubectx` and `mozjs`. A fourth
retired `syslinux` (work remains on branch `pkg-syslinux`), `cppunit`,
`libite`, and both fuse specs. The X11 wave then retired `mkfontdir`
because `mkfontscale` already owns its files, and the final cleanup
retired `rpmlint` (its six Python runtime dependencies are not in the
books or the repo).

The second wave replaced the old `lua-lgi` spec directory with
`package_specs/lgi` (same `Name`/version, plus the Lua 5.4 and
GLib 2.86+ fixes), so `lua-lgi` was removed instead of leaving two specs
for one package.

### 2.2 Deliberately skipped

- **SDL1**: the `sdl`/`sdl-image`/`sdl-ttf` specs were retired on
  2026-11-05. SDL2 2.32.74 and SDL3 3.4.18 are shipped at the book
  versions, and `sdl2-image`/`sdl2-ttf` are shipped from the second
  wave.
- **`mkfontdir`**: retired because `mkfontscale` already provides
  `/usr/bin/mkfontdir` and its man page.

## 3. Newer or older than the book

| package | local | book | status |
|---|---|---|---|
| `db` | 6.2.32 | 5.3.28 | shipped; allowed ("at least the book") |
| `xml-parser` | 2.59 | 2.57 | shipped; allowed ("at least the book") |

`sqlite` 3.54.1 is **not** newer: the book entity `sqlite-version` is the
autoconf build number `3540100`, which equals 3.54.1. The script converts
it; other tools report it as a false mismatch.

## 4. What this audit did not cover

- Cross-compilation and non-x86_64: the repo is x86_64 only.
- Optional BLFS features with no spec (Wayland, PipeWire, printing, …);
  those are product decisions rather than version skew.
- The 111 shipped no-entity packages are not individually
  version-checked beyond the wave-specific checks above;
  `scripts/spec_audit.py` compares whatever the books expose as
  entities.

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
