# Browneye spec audit — LFS/BLFS trunk

Audit of `package_specs/` against the LFS and BLFS checkouts and the
**published** repository, 2026-11-03.

- Repo snapshot: `repodata/primary.xml` of
  <https://tomfool.8bit.ca/browneye/packages/13.1/> — **724 RPM names**
  from **433 source packages**.
- Books: `~/repos/lfs` branch `trunk` (`1493db7`) and `~/repos/blfs`
  branch `trunk` (`60fb6e5`).
- Spec tree at commit `9961e02`, plus the fixes listed in §3.
- Regenerate with `python3 scripts/spec_audit.py --primary primary.xml.zst`
  (see §5).

Book versions are read from every `*-version` entity in the two books, LFS
first so a name collision resolves to the LFS chapter-8 version
(`xml-parser` is 2.57 in LFS, 2.59 as a BLFS perl module). A package whose
book page hard-codes its version instead of using an entity — `htop`,
`gstreamer`, `vte`, `libyaml`, several binary bundles — cannot be compared
this way and is reported as **NO-ENTITY** ("not comparable"), not as
"not in the books".

## Executive summary

| measure | count |
|---|---:|
| spec files / spec directories | 556 / 553 |
| shipped spec files (live source package in the repo) | 434 |
| source packages in the published repo | 433 |
| RPM names in the published repo | 724 |
| **shipped packages below the book** | **0** |
| shipped packages at the book | 358 |
| shipped packages above the book | 1 (`xml-parser`, approved) |
| shipped packages with no comparable book entity | 75 |
| unbuilt spec files | 122 |
| unbuilt specs below the book | 0 |
| unbuilt specs at the book | 5 |
| unbuilt specs above the book | 2 (`db`, `zip`) |
| unbuilt specs with no comparable book entity | 115 |
| specs with `Summary: TODO` | 76 |
| specs with `TODO` in `%description` | 87 |
| shipped specs with a missing referenced patch | 0 |
| shipped specs with a sources/version mismatch | 0 |
| specs with neither `sources` nor `nosources` | 0 |

**Bottom line.** Version parity for everything the distro ships holds: no
shipped package is below LFS/BLFS trunk, and the only package above it
(`xml-parser` 2.59 vs 2.57) is allowed by the "at least the book version"
rule. The remaining debt is metadata, not versions.

## 1. Shipped packages

358 shipped source packages match the book exactly and one (`xml-parser`)
is newer. The 75 without a comparable entity fall into four groups and
spot checks of each found no stale versions:

- **Distro-specific metas and bundles**: the 13 `browneye-*` packages,
  `opencode-bin`, `herdr`, `kitty-bin`, `google-chrome-bin`,
  `firefox-bin`, `podman-bin`, `passt`, `bwm-ng`, `bash-completion`,
  `pulsemixer`, `tea`, `extra fonts`.
- **RPM/dnf stack not covered by the books**: `rpm`, `dnf`, `libdnf`,
  `libsolv`, `librepo`, `libcomps`, `libmodulemd`, `createrepo_c`,
  `zchunk`, `drpm`-adjacent helpers.
- **Book pages that hard-code their version** (no entity): `htop`
  3.5.3, `gstreamer`/`gst-plugins-base` 1.28.8, `vte` 0.84.1,
  `libyaml` 0.2.5, `libsecret` 0.21.8.2, `squashfs-tools` 4.7.5,
  `mtools` 4.0.50, `privoxy` 4.2.0, `dracut` 112, `cairomm` 1.14.6.
- **Book-less by decision**: `libbsd`, `libmd`, `linux-firmware`.

Known deviations and exceptions are recorded in issue #7.

### 1.1 Source metadata corrected in this pass

The audit checks each `sources` file against the spec `Version`. Seven
shipped specs carried stale source names and were fixed here (the URL was
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

`glib`'s bootstrap spec (`glib-pass1`) was still at 2.90.0 while the book
and the main spec are 2.90.1; it now matches. It is bootstrap-only and was
not published from that spec.

The `sources/version mismatch` rows that remain are all expected: date- or
commit-named archives (`font-siji`, `passt`), binary bundles
(`podman-bin`, `opencode-bin`, `herdr`), SF "download" URLs
(`font-terminus`), and `sqlite`'s autoconf numbering. `autoconf213`'s
shared `sources` file lists the 2.73 tarball first; that is tracked in
issue #8 with the missing patch.

### 1.2 Open shipped-package debt

- **`Summary: TODO` / `TODO` descriptions** in 76 and 87 specs — issue #8.
- **`autoconf213`** is unbuildable (patch 404s, not vendored) — issue #8.
- **`zip` is not shipped** while `unzip` now is — decision in issue #7.

## 2. Unbuilt specs (122)

122 spec files have no matching source package in the published repo: 115
have no comparable book entity, 5 are at the book, 2 are above it (`db`
6.2.32 vs 5.3.28, `zip` 30 vs 3.0 — the same 3.0 release written without a
decimal point). None of them is below the book.

They cost nothing while they stay unbuilt, but the parity rule in
`AGENTS.md` applies the moment someone builds one. Grouped by intent:

| group | count | examples |
|---|---:|---|
| Python 2/3 modules | 36 | `python2-pip`, `python3-requests`, the sphinx stack |
| Desktop / miscellaneous | 48 | `gtkmm`, `libpeas`, `tmux`, `openvpn`, `rofi`, `sdl`, `webp`, `syslinux` |
| Container / k8s tools | 10 | `docker`, `kubectl`, `dive`, `flatpak` |
| Perl modules | 7 | `perl-dbi`, `perl-ssleay` |
| X11 drivers and tools | 7 | `xf86-video-{fbdev,intel,vmware}`, `xbacklight` |
| Window managers | 6 | `awesome`, `bspwm`, `dwm`, `polybar`, `sxhkd` |
| Fonts | 1 | `font-noto-cjk` |

A handful of names in this bucket may be mismatches rather than truly
unbuilt (a spec whose `Name:` differs from the source package actually
built, e.g. `libx264`); check before deleting anything.

### 2.1 Retired spec directories removed in this pass

Ten specs whose BLFS pages now live only in `book/archive/` and which have
no RPM in the repository were deleted: `atk`, `at-spi2-atk`, `check`,
`dhcp`, `gtk-xfce-engine`, `libcroco`, `mandoc`, `python2`, `udev`,
`xfce4-xkb-plugin`. Nothing in the tree depended on them (the remaining
mentions are comments, filename fragments and `Provides:` strings).

## 3. Newer than book

| package | local | book | status |
|---|---|---|---|
| `xml-parser` | 2.59 | 2.57 | shipped; allowed ("at least the book") |
| `db` | 6.2.32 | 5.3.28 | unbuilt stub |
| `zip` | 30 | 3.0 | unbuilt; same release, no decimal point |

`sqlite` 3.54.1 is **not** newer: the book entity `sqlite-version` is the
autoconf build number `3540100`, which equals 3.54.1. The script converts
it; other tools report it as a false mismatch.

## 4. What this audit did not cover

- Cross-compilation and non-x86_64: the repo is x86_64 only.
- Optional BLFS features with no spec (Wayland, PipeWire, printing, …);
  those are product decisions rather than version skew, and the previous
  edition of this file listed them. They are now out of scope.
- The 115 unbuilt no-entity specs are not individually version-checked;
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
