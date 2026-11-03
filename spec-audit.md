# Browneye spec audit — LFS/BLFS r13.1 trunk

Read-only audit of `package_specs/` against the current LFS and BLFS
checkouts. No spec, RPM, repo, rootfs, image or `plan.md` file was changed.

- Audit worktree: `/home/daspork/browneye-spec-audit`, branch `spec-audit`
  (base commit `9d7fcf9`).
- Books read: `~/repos/lfs` branch `trunk` (`581459fa3`) and `~/repos/blfs`
  branch `trunk` (`4fd113e1c6`), both the r13.1 line.
- RPMs read: `build/repo-all` (282 RPMs, read-only).
- Date of audit: 2026-11-01.

> Note (2026-11-03): the browser wave removed `chromium-bin` and added
> `google-chrome-bin`, `xdg-utils` and `liberation-fonts`.  This audit is a
> 2026-11-01 snapshot; its counts were not re-run.  The binary-only row below
> names the replacement browser package.

## Executive summary

| measure | count |
|---|---:|
| spec files / spec directories | 532 / 530 |
| unique spec `Name:` values | 531 (`glib` has two spec files) |
| source packages shipped in `build/repo-all` | 256 |
| RPMs in `build/repo-all` (including subpackages) | 282 |
| shipped source packages **below** book | **0** |
| shipped source packages at book | 227 |
| shipped source packages above book | 2 (`nodejs`, `rust`; approved) |
| shipped source packages with no book counterpart | 27 |
| specs not represented in `build/repo-all` at all | 276 |
| spec-only packages **below** book | **154** |
| spec-only packages at book | 16 |
| spec-only packages above book (real) | 1 (`db`); 2 format artifacts |
| spec-only packages with no book counterpart / retired | 103 |
| LFS chapter-8 systemd base specs missing | **0** (80/80) |
| desktop build-stack specs missing | **0** (97/97) |

**Bottom line.** Version parity for everything the distro actually ships is
holding: no shipped source package is below LFS/BLFS trunk. The backlog is
almost entirely the 276 legacy specs that are not built, of which 154 are
below the book. The real shipped defects are not version skew but
build/repo staleness and source metadata: five shipped specs are newer than
the RPM in `build/repo-all`, three shipped specs have a `sources` file that
points at an older tarball than their `Version:`, `lua` references a patch
that is not in the tree, and the shipped `system-minimal` meta requires five
packages that are not in the repo.

## 1. Not-updated shipped packages

**There are no shipped packages below the book version.** All 229 shipped
source packages that have a book counterpart are at or above it (227 equal,
2 approved newer).

For completeness, the shipped packages with other defects, highest impact
first:

| priority | package(s) | finding | evidence |
|---|---|---|---|
| P0 | `system-minimal` | shipped meta has five unsatisfiable `Requires:`; depends on the removed sysv/finit path | asks for `NetworkManager`, `dhcp`, `finit`, `sysklogd`, `wpa-supplicant`; none are in `build/repo-all` |
| P1 | `cpio` | spec 2.15 but `sources` still fetches 2.13 | `package_specs/cpio/sources` = `cpio-2.13.tar.gz`; local `SOURCES` has `cpio-2.15.tar.bz2` |
| P1 | `dracut` | spec 112 but `sources` still fetches 2019-era dracut 050 | `package_specs/dracut/sources` = `dracut-050.tar.xz`; spec comment has the 112 URL |
| P1 | `linux-firmware` | spec 20261019 but `sources` fetches 20230515; `Source2` wireless-regdb is not tracked | `linux-firmware/sources` = `linux-firmware-20230515.tar.xz`; `Source2` only in the spec comment |
| P1 | `mesa`, `python`, `linux-firmware`, `system-minimal`, `xfce-desktop` | spec `Version-Release` is newer than the RPM in the repo | see §6 |
| P2 | `lua` | `%prep` references `lua-5.4.8-shared_library-1.patch`, absent from `files/` and `sources` | only present in `~/rpmbuild/SOURCES` |
| P2 | `libbsd`, `libmd` | shipped NO-BOOK packages not covered by the exceptions listed in the task | also required by `browneye-base` |
| P2 | `xf86-video-vesa` | book moved the page to `archive/`; still shipped because QEMU needs it | archive version 2.3.3 equals local |
| P3 | `coreutils` | stale `Patch:` header (8.30) while `%prep` uses the 9.11 patch | `Patch: coreutils-8.30-i18n-1.patch` is dead metadata |
| P3 | 81 shipped specs | no static `%files -f` list; 175 shipped specs do use one | no dangling filelist reference was found |

## 2. Not-updated spec-only packages (154)

All rows are **not shipped** (no RPM in `build/repo-all`). `local` is
`Version-Release` from the spec; `delta` names the first differing component
(`scheme` means the two sides use different version schemes, e.g. a date vs
`1.1.1`). `LFS spec-only` is a package from the LFS book that the systemd
variant does not build.

| # | spec / package | local | book | delta | category | shipped |
|---|---|---|---|---|---|---|
| 1 | `acpid` / acpid | 2.0.28-3 | 2.0.34 | patch | BLFS spec-only | no |
| 2 | `adwaita-icon-theme` / adwaita-icon-theme | 3.30.1-1 | 51.0 | major | BLFS spec-only | no |
| 3 | `alsa-lib` / alsa-lib | 1.1.6-1 | 1.2.16.1 | minor | BLFS spec-only | no |
| 4 | `alsa-plugins` / alsa-plugins | 1.1.6-1 | 1.2.12 | minor | BLFS spec-only | no |
| 5 | `alsa-utils` / alsa-utils | 1.2.2-1 | 1.2.16 | patch | BLFS spec-only | no |
| 6 | `appstream-glib` / appstream-glib | 0.7.16-1 | 0.8.4 | minor | BLFS spec-only | no |
| 7 | `atkmm` / atkmm | 2.28.3-1 | 2.28.5 | patch | BLFS spec-only | no |
| 8 | `bdftopcf` / bdftopcf | 1.1-1 | 1.1.1 | patch | BLFS spec-only | no |
| 9 | `bubblewrap` / bubblewrap | 0.4.0-1 | 0.13.0 | minor | BLFS spec-only | no |
| 10 | `cairomm` / cairomm | 1.12.2-1 | 1.14.6 | minor | BLFS spec-only | no |
| 11 | `cups` / cups | 2.3.3-1 | 2.4.19 | minor | BLFS spec-only | no |
| 12 | `dbus-glib` / dbus-glib | 0.110-1 | 0.114 | minor | BLFS spec-only | no |
| 13 | `dconf` / dconf | 0.28.0-1 | 51.0 | major | BLFS spec-only | no |
| 14 | `efivar` / efivar | 38-1 | 39 | major | BLFS spec-only | no |
| 15 | `enchant` / enchant | 2.2.11-1 | 2.8.21 | minor | BLFS spec-only | no |
| 16 | `ffmpeg` / ffmpeg | 4.1.1-1 | 9.0.2 | major | BLFS spec-only | no |
| 17 | `flac` / flac | 1.3.2-1 | 1.5.0 | minor | BLFS spec-only | no |
| 18 | `font-adobe-utopia-type1` / font-adobe-utopia-type1 | 1.0.4-1 | 1.0.5 | patch | BLFS spec-only | no |
| 19 | `font-bh-type1` / font-bh-type1 | 1.0.3-1 | 1.0.4 | patch | BLFS spec-only | no |
| 20 | `font-ibm-type1` / font-ibm-type1 | 1.0.3-1 | 1.0.4 | patch | BLFS spec-only | no |
| 21 | `font-misc-ethiopic` / font-misc-ethiopic | 1.0.3-1 | 1.0.5 | patch | BLFS spec-only | no |
| 22 | `font-ttf-unifont` / font-ttf-unifont | 12.1.04-1 | 17.0.03 | major | BLFS spec-only | no |
| 23 | `font-xfree86-type1` / font-xfree86-type1 | 1.0.4-1 | 1.0.5 | patch | BLFS spec-only | no |
| 24 | `freeglut` / freeglut | 3.4.0-1 | 3.8.0 | minor | BLFS spec-only | no |
| 25 | `fuse` / fuse | 3.2.5-1 | 3.18.3 | minor | BLFS spec-only | no |
| 26 | `libgcr` / gcr | 3.28.1-1 | 3.41.2 | minor | BLFS spec-only | no |
| 27 | `giflib` / giflib | 5.2.1-1 | 6.1.3 | major | BLFS spec-only | no |
| 28 | `glew` / glew | 2.1.0-1 | 2.3.1 | minor | BLFS spec-only | no |
| 29 | `glib-networking` / glib-networking | 2.56.1-1 | 2.90.0 | minor | BLFS spec-only | no |
| 30 | `glibmm` / glibmm | 2.66.5-1 | 2.66.10 | patch | BLFS spec-only | no |
| 31 | `gnupg` / gnupg | 2.2.9-1 | 2.5.24 | minor | BLFS spec-only | no |
| 32 | `gsettings-desktop-schemas` / gsettings-desktop-schemas | 3.28.0-1 | 51.0 | major | BLFS spec-only | no |
| 33 | `gst-plugins-base` / gst-plugins-base | 1.16.2-1 | 1.28.7 | minor | BLFS spec-only | no |
| 34 | `gstreamer` / gstreamer | 1.16.2-1 | 1.28.7 | minor | BLFS spec-only | no |
| 35 | `gtkmm` / gtkmm | 3.24.8-1 | 3.24.11 | patch | BLFS spec-only | no |
| 36 | `icewm` / icewm | 3.4.1-1 | 4.1.0 | major | BLFS spec-only | no |
| 37 | `imlib2` / imlib2 | 1.12.0-1 | 1.12.7 | patch | BLFS spec-only | no |
| 38 | `iptables` / iptables | 1.8.0-1 | 1.8.13 | patch | BLFS spec-only | no |
| 39 | `json-glib` / json-glib | 1.4.2-1 | 1.10.8 | minor | BLFS spec-only | no |
| 40 | `libaio` / libaio | 0.3.112-1 | 0.3.113 | patch | BLFS spec-only | no |
| 41 | `libass` / libass | 0.14.0-1 | 0.17.5 | minor | BLFS spec-only | no |
| 42 | `libevent` / libevent | 2.1.12-1 | 2.1.13 | patch | BLFS spec-only | no |
| 43 | `libfs` / libfs | 1.0.9-1 | 1.0.10 | patch | BLFS spec-only | no |
| 44 | `libgcrypt` / libgcrypt | 1.10.2-1 | 1.12.4 | minor | BLFS spec-only | no |
| 45 | `libglu` / libglu | 9.0.1-1 | 9.0.3 | patch | BLFS spec-only | no |
| 46 | `libksba` / libksba | 1.3.5-1 | 1.8.1 | minor | BLFS spec-only | no |
| 47 | `libndp` / libndp | 1.7-1 | 1.9 | minor | BLFS spec-only | no |
| 48 | `libnl` / libnl | 3.4.0-1 | 3.12.0 | minor | BLFS spec-only | no |
| 49 | `libopus` / libopus | 1.3-1 | 1.6.1 | minor | BLFS spec-only | no |
| 50 | `libpeas` / libpeas | 1.26.0-1 | 1.38.1 | minor | BLFS spec-only | no |
| 51 | `libpoppler` / libpoppler | 0.88.0-1 | 26.09.0 | major | BLFS spec-only | no |
| 52 | `libportal` / libportal | 0.3-1 | 0.9.1 | minor | BLFS spec-only | no |
| 53 | `librsvg` / librsvg | 2.44.12-1 | 2.63.2 | minor | BLFS spec-only | no |
| 54 | `libsecret` / libsecret | 0.21.0-1 | 0.21.8.2 | patch | BLFS spec-only | no |
| 55 | `libsigc++` / libsigc++ | 2.10.3-1 | 2.12.1 | minor | BLFS spec-only | no |
| 56 | `libsndfile` / libsndfile | 1.0.28-1 | 1.2.2 | minor | BLFS spec-only | no |
| 57 | `libssh2` / libssh2 | 1.8.0-1 | 1.11.1 | minor | BLFS spec-only | no |
| 58 | `libvpx` / libvpx | 1.8.0-1 | 1.17.0 | minor | BLFS spec-only | no |
| 59 | `libx264` / libx264 | 20190815-1 | 20250815 | scheme | BLFS spec-only | no |
| 60 | `libx265` / libx265 | 3.0-1 | 4.3 | major | BLFS spec-only | no |
| 61 | `libxaw` / libxaw | 1.0.15-1 | 1.0.16 | patch | BLFS spec-only | no |
| 62 | `libxpm` / libxpm | 3.5.16-1 | 3.5.19 | patch | BLFS spec-only | no |
| 63 | `libxscrnsaver` / libxscrnsaver | 1.2.4-1 | 1.2.5 | patch | BLFS spec-only | no |
| 64 | `libxv` / libxv | 1.0.12-1 | 1.0.13 | patch | BLFS spec-only | no |
| 65 | `libxvmc` / libxvmc | 1.0.13-1 | 1.0.15 | patch | BLFS spec-only | no |
| 66 | `libxxf86dga` / libxxf86dga | 1.1.6-1 | 1.1.7 | patch | BLFS spec-only | no |
| 67 | `lightdm` / lightdm | 1.24.0-1 | 1.33.1 | minor | BLFS spec-only | no |
| 68 | `lightdm-gtk-greeter` / lightdm-gtk-greeter | 2.0.8-1 | 2.0.9 | patch | BLFS spec-only | no |
| 69 | `luit` / luit | 1.1.1-1 | 20260907 | scheme | BLFS spec-only | no |
| 70 | `lvm2` / LVM2 | 2.03.05-1 | 2.03.42 | patch | BLFS spec-only | no |
| 71 | `nasm` / nasm | 2.14.02-1 | 3.02 | major | BLFS spec-only | no |
| 72 | `net-tools` / net-tools | 1.60-1 | 2.10 | major | BLFS spec-only | no |
| 73 | `network-manager-applet` / network-manager-applet | 1.8.22-1 | 1.34.0 | minor | BLFS spec-only | no |
| 74 | `networkmanager` / NetworkManager | 1.42.4-1 | 1.58.1 | minor | BLFS spec-only | no |
| 75 | `newt` / newt | 0.52.20-2 | 0.52.25 | patch | BLFS spec-only | no |
| 76 | `npth` / npth | 1.6-1 | 1.8 | minor | BLFS spec-only | no |
| 77 | `nspr` / nspr | 4.35-1 | 4.40 | minor | BLFS spec-only | no |
| 78 | `nss` / nss | 3.92-1 | 3.130 | minor | BLFS spec-only | no |
| 79 | `ntp` / ntp | 4.2.8p14-2 | 4.2.8p18 | patch | BLFS spec-only | no |
| 80 | `openjpeg` / openjpeg | 2.3.1-1 | 2.5.4 | minor | BLFS spec-only | no |
| 81 | `pangomm` / pangomm | 2.46.3-1 | 2.46.5 | patch | BLFS spec-only | no |
| 82 | `pavucontrol` / pavucontrol | 3.0-1 | 6.2 | major | BLFS spec-only | no |
| 83 | `pciutils` / pciutils | 3.6.4-1 | 3.15.0 | minor | BLFS spec-only | no |
| 84 | `perl-io-sockets-ssl` / perl-io-sockets-ssl | 2.068-1 | 2.099 | minor | BLFS spec-only | no |
| 85 | `perl-uri` / perl-uri | 1.74-1 | 5.37 | major | BLFS spec-only | no |
| 86 | `pulseaudio` / pulseaudio | 12.2-1 | 17.0 | major | BLFS spec-only | no |
| 87 | `python-mako` / python-mako | 1.2.4-1 | 1.4.3 | minor | BLFS spec-only | no |
| 88 | `python-cairo` / python-pycairo | 1.24.0-1 | 1.29.1 | minor | BLFS spec-only | no |
| 89 | `python-pygobject` / python-pygobject | 3.44.1-1 | 3.58.0 | minor | BLFS spec-only | no |
| 90 | `python-pyparsing` / python-pyparsing | 2.4.5-1 | 3.3.3 | major | BLFS spec-only | no |
| 91 | `python-six` / python-six | 1.13.0-1 | 1.17.0 | minor | BLFS spec-only | no |
| 92 | `python-sphinx` / python-sphinx | 2.2.2-1 | 9.1.0 | major | BLFS spec-only | no |
| 93 | `python3-alabaster` / python3-alabaster | 0.7.12-1 | 1.0.0 | major | BLFS spec-only | no |
| 94 | `python3-babel` / python3-babel | 2.8.0-1 | 2.18.0 | minor | BLFS spec-only | no |
| 95 | `python3-certifi` / python3-certifi | 2020.4.5.1-1 | 2026.6.17 | major | BLFS spec-only | no |
| 96 | `python3-chardet` / python3-chardet | 3.0.4-1 | 5.2.0 | major | BLFS spec-only | no |
| 97 | `python3-idna` / python3-idna | 2.9-1 | 3.18 | major | BLFS spec-only | no |
| 98 | `python3-imagesize` / python3-imagesize | 1.1.0-1 | 1.4.1 | minor | BLFS spec-only | no |
| 99 | `python3-pygments` / python3-pygments | 2.6.1-1 | 2.21.0 | minor | BLFS spec-only | no |
| 100 | `python3-pytz` / python3-pytz | 2020.1-1 | 2026.2 | major | BLFS spec-only | no |
| 101 | `python3-requests` / python3-requests | 2.23.0-1 | 2.34.2 | minor | BLFS spec-only | no |
| 102 | `python3-snowball` / python3-snowballstemmer | 1.9.0-1 | 3.1.1 | major | BLFS spec-only | no |
| 103 | `python3-sphinxcontrib-applehelp` / python3-sphinxcontrib-applehelp | 1.0.2-1 | 2.0.0 | major | BLFS spec-only | no |
| 104 | `python3-sphinxcontrib-devhelp` / python3-sphinxcontrib-devhelp | 1.0.2-1 | 2.0.0 | major | BLFS spec-only | no |
| 105 | `python3-sphinxcontrib-htmlhelp` / python3-sphinxcontrib-htmlhelp | 1.0.3-1 | 2.1.0 | major | BLFS spec-only | no |
| 106 | `python3-sphinxcontrib-qthelp` / python3-sphinxcontrib-qthelp | 1.0.3-1 | 2.0.0 | major | BLFS spec-only | no |
| 107 | `python3-sphinxcontrib-serializinghtml` / python3-sphinxcontrib-serializinghtml | 1.1.4-1 | 2.0.0 | major | BLFS spec-only | no |
| 108 | `python3-urllib3` / python3-urllib3 | 1.25.9-1 | 2.7.0 | major | BLFS spec-only | no |
| 109 | `qemu` / qemu | 8.1.0-1 | 11.1.1 | major | BLFS spec-only | no |
| 110 | `ruby` / ruby | 2.7.1-1 | 4.0.7 | major | BLFS spec-only | no |
| 111 | `rxvt-unicode` / rxvt-unicode | 9.22-1 | 9.31 | minor | BLFS spec-only | no |
| 112 | `screen` / screen | 4.8.0-1 | 5.0.2 | major | BLFS spec-only | no |
| 113 | `sdl2` / sdl2 | 2.0.8-1 | 2.32.72 | minor | BLFS spec-only | no |
| 114 | `sessreg` / sessreg | 1.1.1-1 | 1.1.4 | patch | BLFS spec-only | no |
| 115 | `setxkbmap` / setxkbmap | 1.3.1-1 | 1.3.5 | patch | BLFS spec-only | no |
| 116 | `slang` / slang | 2.3.2-1 | 2.3.3 | patch | BLFS spec-only | no |
| 117 | `smproxy` / smproxy | 1.0.6-1 | 1.0.8 | patch | BLFS spec-only | no |
| 118 | `stunnel` / stunnel | 5.69-1 | 5.82 | minor | BLFS spec-only | no |
| 119 | `sudo` / sudo | 1.8.23-1 | 1.9.17p2 | minor | BLFS spec-only | no |
| 120 | `sysklogd` / sysklogd | 1.5.1-1 | 2.7.2 | major | LFS spec-only | no |
| 121 | `usbutils` / usbutils | 012-1 | 019 | major | BLFS spec-only | no |
| 122 | `vala` / vala | 0.40.8-1 | 0.56.19 | minor | BLFS spec-only | no |
| 123 | `webp` / webp | 1.1.0-1 | 1.6.0 | minor | BLFS spec-only | no |
| 124 | `wget` / wget | 1.20.1-1 | 1.25.0 | minor | BLFS spec-only | no |
| 125 | `wpa-supplicant` / wpa-supplicant | 2.7-1 | 2.12 | minor | BLFS spec-only | no |
| 126 | `xbitmaps` / xbitmaps | 1.1.2-1 | 1.1.4 | patch | BLFS spec-only | no |
| 127 | `xcb-util-cursor` / xcb-util-cursor | 0.1.4-1 | 0.1.6 | patch | BLFS spec-only | no |
| 128 | `xcmsdb` / xcmsdb | 1.0.5-1 | 1.0.7 | patch | BLFS spec-only | no |
| 129 | `xcursor-themes` / xcursor-themes | 1.0.6-1 | 1.0.7 | patch | BLFS spec-only | no |
| 130 | `xcursorgen` / xcursorgen | 1.0.7-1 | 1.0.9 | patch | BLFS spec-only | no |
| 131 | `xdg-dbus-proxy` / xdg-dbus-proxy | 0.1.2-1 | 0.1.9 | patch | BLFS spec-only | no |
| 132 | `xdg-desktop-portal` / xdg-desktop-portal | 1.8.0-1 | 1.22.1 | minor | BLFS spec-only | no |
| 133 | `xdpyinfo` / xdpyinfo | 1.3.2-1 | 1.4.0 | minor | BLFS spec-only | no |
| 134 | `xdriinfo` / xdriinfo | 1.0.6-1 | 1.0.8 | patch | BLFS spec-only | no |
| 135 | `xev` / xev | 1.2.2-1 | 1.2.7 | patch | BLFS spec-only | no |
| 136 | `xf86-input-synaptics` / xf86-input-synaptics | 1.9.1-1 | 1.10.0 | minor | BLFS spec-only | no |
| 137 | `xgamma` / xgamma | 1.0.6-1 | 1.0.8 | patch | BLFS spec-only | no |
| 138 | `xinput` / xinput | 1.6.2-1 | 1.6.4 | patch | BLFS spec-only | no |
| 139 | `xkbevd` / xkbevd | 1.1.4-1 | 1.1.6 | patch | BLFS spec-only | no |
| 140 | `xkbutils` / xkbutils | 1.0.4-1 | 1.0.7 | patch | BLFS spec-only | no |
| 141 | `xkill` / xkill | 1.0.5-1 | 1.0.7 | patch | BLFS spec-only | no |
| 142 | `xlsatoms` / xlsatoms | 1.1.2-1 | 1.1.5 | patch | BLFS spec-only | no |
| 143 | `xlsclients` / xlsclients | 1.1.4-1 | 1.1.6 | patch | BLFS spec-only | no |
| 144 | `xmessage` / xmessage | 1.0.5-1 | 1.0.7 | patch | BLFS spec-only | no |
| 145 | `xml-parser` / xml-parser | 2.46-1 | 2.57 | minor | LFS spec-only | no |
| 146 | `xorriso` / xorriso | 1.5.6-1 | 1.5.8.pl02 | patch | BLFS spec-only | no |
| 147 | `xpr` / xpr | 1.0.5-1 | 1.2.1 | minor | BLFS spec-only | no |
| 148 | `xprop` / xprop | 1.2.3-1 | 1.2.8 | patch | BLFS spec-only | no |
| 149 | `xrandr` / xrandr | 1.5.0-1 | 1.5.4 | patch | BLFS spec-only | no |
| 150 | `xrefresh` / xrefresh | 1.0.6-1 | 1.1.1 | minor | BLFS spec-only | no |
| 151 | `xsetroot` / xsetroot | 1.1.2-1 | 1.1.4 | patch | BLFS spec-only | no |
| 152 | `xterm` / xterm | 344-1 | 411 | major | BLFS spec-only | no |
| 153 | `xvinfo` / xvinfo | 1.1.3-1 | 1.1.6 | patch | BLFS spec-only | no |
| 154 | `xwud` / xwud | 1.0.5-1 | 1.0.8 | patch | BLFS spec-only | no |

## 3. NO-BOOK specs

These have no current LFS/BLFS entity. They are separated from the
version-skew tables so that they are not mistaken for "outdated" versions.

### 3.1 Shipped NO-BOOK packages (27)

| package | spec version | category | status |
|---|---|---|---|
| `browneye-base` | 13.1-4 | browneye glue/meta | custom distro meta |
| `browneye-basefs` | 1.0-1 | browneye glue/meta | custom distro glue |
| `browneye-build` | 13.1-1 | browneye glue/meta | custom build meta (E1) |
| `browneye-desktop-config` | 13.1-1 | browneye glue/meta | custom desktop config |
| `browneye-firstboot` | 13.1-1 | browneye glue/meta | custom E5 service |
| `browneye-release` | 13.1-1 | browneye glue/meta | custom distro release |
| `browneye-rpm-config` | 13.1-1 | browneye glue/meta | custom rpm macros |
| `browneye-sysconfig` | 13.1-2 | browneye glue/meta | custom distro config |
| `browneye-workstation` | 13.1-1 | browneye glue/meta | custom workstation meta (D20) |
| `createrepo_c` | 1.2.6-1 | E1 build stack (approved D22) | approved |
| `dnf` | 4.24.0-1 | E1 build stack (approved D22) | approved |
| `libcomps` | 0.1.24-1 | E1 build stack (approved D22) | approved |
| `libdnf` | 0.76.0-1 | E1 build stack (approved D22) | approved |
| `libmodulemd` | 2.15.3-1 | E1 build stack (approved D22) | approved |
| `librepo` | 1.21.3-1 | E1 build stack (approved D22) | approved |
| `libsolv` | 0.7.41-1 | E1 build stack (approved D22) | approved |
| `rpm` | 4.18.1-2 | E1 build stack (approved D22) | approved |
| `zchunk` | 1.5.5-1 | E1 build stack (approved D22) | approved |
| `dracut` | 112-1 | initramfs (plan D11) | plan-approved, not in the task's exception list |
| `linux-firmware` | 20261019-3 | firmware (approved D10) | approved curated snapshot |
| `herdr` | 0.9.5-1 | prebuilt agent binary (approved D19) | approved |
| `opencode-bin` | 2.2.5-1 | prebuilt agent binary (approved D19) | approved |
| `system-minimal` | 0.1-3 | custom meta | stale/unused; unresolved requires |
| `xfce-desktop` | 4.20-4 | custom desktop meta | custom meta |
| `libbsd` | 0.12.2-1 | base dependency | **NO-BOOK; not in the listed exceptions** |
| `libmd` | 1.3.0-1 | base dependency | **NO-BOOK; not in the listed exceptions** |
| `xf86-video-vesa` | 2.3.3-1 | Xorg driver | moved to book `archive/`; still needed by QEMU |

Notes on the approved exceptions (not defects):

- Node.js is **26.13.0** under `/opt` (D17); the book is 26.9.0.
- Rust is **1.99.0** under `/opt` (D31); the book is 1.98.1.
- `opencode-bin` 2.2.5 and `herdr` 0.9.5 are prebuilt binaries (D19).
- `linux-firmware` is the curated 20261019 snapshot (D10).
- `dnf` 4.24.0, `libdnf`, `librepo`, `libcomps`, `libmodulemd`, `libsolv`,
  `zchunk`, `createrepo_c` 1.2.6 and `rpm` 4.18.1 are the E1 toolchain (D22).
- `dracut` 112 is a plan decision (D11); it has no current BLFS package page.
- `libbsd` and `libmd` are **not** in the current LFS/BLFS books and are not
  in the task's approved-exception list. They are shipped and required by
  `browneye-base`; flagged for a user decision, not classified as a version
  defect.

### 3.2 Spec-only NO-BOOK / retired packages (103)

| category | count | packages |
|---|---:|---|
| Retired/duplicate of a current package | 5 | `fuse2`, `pcre`, `sdl`, `sqlite3`, `libsoup` (libsoup2) |
| Archived by the current book (page only in `archive/`) | 10 | `atk`, `at-spi2-atk`, `check`, `dhcp`, `gtk-xfce-engine`, `libcroco`, `mandoc`, `python2`, `udev`, `xfce4-xkb-plugin` |
| Prebuilt/binary-only tools | 10 | `google-chrome-bin`, `firefox-bin`, `go-bin`, `kdevelop-bin`, `kubectl`, `kubectx`, `podman-bin`, `transgui-bin`, `dive`, `gotop` |
| E1/legacy build tooling | 5 | `dnf-plugins-core`, `drpm`, `rpmlint`, `build-essential`, `fakeroot-ng` |
| Python 2 / old Python modules | 13 | `python2-pip`, `python2-psutil`, `python2-pycairo`, `python2-pycurl`, `python2-pygobject`, `python2-setuptools`, `python-pip`, `python-distro`, `python-scikit-build`, `python3-dateutil`, `python3-importlib_metadata`, `python3-pygpgme`, `python3-zipp` |
| Perl modules not in the current book | 5 | `perl-cgi`, `perl-crypt-password-md5`, `perl-dbi`, `perl-digest-sha1`, `perl-ssleay` |
| Fonts not carried as versioned book packages | 4 | `font-noto-cjk`, `font-siji`, `font-terminus`, `font-ubuntu-font-family` |
| Xorg drivers archived by the book | 4 | `xf86-video-amdgpu`, `xf86-video-fbdev`, `xf86-video-intel`, `xf86-video-vmware` |
| Other legacy/extra distro packages | 47 | `acpi`, `awesome`, `bash-completion`, `bspwm`, `busybox`, `bwm-ng`, `cdrkit`, `cppunit`, `docker`, `docker-compose`, `dunst`, `dwm`, `eudev`, `finit`, `flatpak`, `help2man`, `htop`, `libdmx`, `libite`, `libostree`, `libstemmer`, `libuev`, `libxdg-basedir`, `lgi`, `mkfontdir`, `mozjs`, `mtools`, `ncdu`, `numactl`, `openvpn`, `polybar`, `proxychains-ng`, `rofi`, `sdl-image`, `sdl-ttf`, `sdl2-image`, `sdl2-ttf`, `squashfs-tools`, `sxhkd`, `syslinux`, `terminator`, `tmux`, `tzdb`, `wmname`, `x11perf`, `xbacklight`, `xcb-util-xrm` |
| **total** | **103** | |

`libsoup` is the libsoup2 branch and is not comparable to the book's
libsoup3; it is listed as retired rather than outdated. The
`python3-sphinxcontrib-jsmath` spec (1.0.1) equals the book's
`sc-jsmath-version` and is therefore counted with the 16 "at book"
spec-only packages, not here.

## 4. Missing specs

### 4.1 Base and built desktop scope

No spec is missing from either scope:

- **LFS chapter 8, systemd variant:** 80/80 packages have a spec and are
  represented by RPMs in `build/repo-all` (`dbus` is represented by its
  `dbus-daemon`, `dbus-libs` and `dbus-x11` subpackages). The sysv-only
  pages (`udev`, `sysklogd`, `sysvinit`) are not required by this variant;
  specs for `udev` and `sysklogd` exist anyway. `intltool` and `xml-parser`
  are commented out in the LFS chapter and also have specs.
- **Desktop build stack:** all 97 package names used by
  `scripts/build_blfs_stack.sh` have a spec directory. XFCE 4.20 core,
  Xorg/X11, Mesa and the desktop dependencies are complete for what the
  build actually ships.

### 4.2 Optional/feature gaps (no spec at all)

These BLFS packages have no spec and are not in the current build closure.
None is required for the current `browneye-base`, `browneye-workstation` or
`xfce-desktop` metas; each is an optional feature gap.

| package | book version | why it matters | current handling |
|---|---|---|---|
| `libidn2` | 2.3.8 | IDN for curl/rsync/wget | not built; `rsync --disable-idn` |
| `libpsl` | 0.23.3 | Public Suffix List for curl | not built; `curl --without-libpsl` |
| `glycin` | 2.2.1 | gdk-pixbuf loader backend | not built; gdk-pixbuf keeps PNG/JPEG only |
| `docbook-xsl` | 1.79.2 | man/doc generation | only `docbook-xsl-nons` has a spec; xfce4-terminal uses `-Ddoc=false` |
| `libwacom` | 2.20.0 | libinput tablet data | not built |
| `elogind` | 257.16 | session/seat management | not built; polkit uses shadow auth |
| `pipewire` | 1.6.9 | audio server | not built |
| `wireplumber` | 0.5.17 | PipeWire session manager | not built |
| `bluez` | 5.87 | Bluetooth | not built |
| `gvfs` | 1.62.0 | XFCE virtual filesystem | not built |
| `udisks2` | 2.11.2 | removable media | not built |
| `accountsservice` | 26.27.3 | user account service | not built |
| `colord` | 1.4.8 | colour management | not built |
| `gnome-keyring` | 51.1 | secrets/keyring | not built |
| `poppler` | 26.09.0 | PDF rendering | only `libpoppler` 0.88.0 spec exists, not built |
| `poppler-data` | — | PDF data files | not built |
| `cups-filters` | 2.0.1 | printing filters | `cups` spec exists, not built |
| `libgsf` | 1.14.59 | GNOME structured files | not built |
| `wayland`, `xwayland` | 1.26.0 / 24.1.13 | Wayland/XWayland | intentionally excluded (D6, X11-only) |

Specs that exist but are not built (not "missing specs"): `librsvg`
2.44.12 (SVG loader, needed by the plan's known desktop gap), `lightdm`
1.24.0, `networkmanager` 1.42.4, `cups` 2.3.3, `pulseaudio` 12.2,
`xf86-video-amdgpu` 23.0.0, `pavucontrol` 3.0. These are all in §2.

## 5. Other staleness

| area | finding | evidence |
|---|---|---|
| Pin file | `lfs.lock` is generated from the r13.1 **tag** (`71ef60ba`), not trunk; 12 base entries are below the current book | `man-pages` 6.18/6.19, `iana-etc` 20260805/20260911, `xz` 5.8.3/5.8.4, `pcre` 10.47/10.48, `pkgconf` 3.0.5/3.0.7, `expat` 2.8.3/2.8.4, `automake` 1.18.1/1.19, `openssl` 4.0.1/4.0.2, `libelf` 0.195/0.196, `iproute2` 7.1.0/7.2.0, `vim` 9.2.1025/9.2.1099, `systemd` 261.2/261.3 |
| Sync tooling | `scripts/sync_lfs_spec.py` reads `lfs.lock`, so `--all-base` would try to downgrade those 12 specs to the r13.1 tag | `sync_lfs_spec.py:104-107` |
| Source URL vs version | `cpio` spec 2.15, `sources` 2.13 | `package_specs/cpio/sources` |
| Source URL vs version | `dracut` spec 112, `sources` 050 | `package_specs/dracut/sources` |
| Source URL vs version | `linux-firmware` spec 20261019, `sources` 20230515; `Source2` not in `sources` | `package_specs/linux-firmware/sources` |
| Source URL vs version | `autoconf213` spec 2.13, `sources` 2.73 | `package_specs/autoconf/sources` |
| Source URL vs version | `dnf-plugins-core` spec 4.4.2, `sources` 4.2.2 | `package_specs/dnf-plugins-core/sources` |
| Source URL vs version | `sqlite3` spec 3.24.0, `sources` 3530400 (3.53.4) | retired duplicate |
| Source URL vs version | `fuse`/`fuse2` spec source URLs are swapped: `fuse` 3.2.5 points at `fuse-2.9.7`, `fuse2` 2.9.7 points at `fuse-3.2.5` | `package_specs/fuse/sources` |
| Missing referenced patch | `lua` references `lua-5.4.8-shared_library-1.patch`; not in `files/` or `sources` | only in `~/rpmbuild/SOURCES` |
| Missing referenced patch | `unzip` references `unzip-6.0-consolidated_fixes-1.patch`; not in the tree | spec-only package |
| Missing referenced patch | `autoconf213` references `autoconf-2.13-consolidated_fixes-1.patch`; not in the tree | spec-only package |
| Stale patch metadata | `coreutils` still has `Patch: coreutils-8.30-i18n-1.patch`; `%prep` applies the 9.11 patch | dead header, not a build failure |
| Source-less specs | 3 shipped specs have neither `sources` nor `nosources`: `browneye-build`, `browneye-desktop-config`, `xfce-desktop` | the other 6 source-less specs correctly use `nosources` |
| Repo drift | 5 shipped specs are newer than their RPM in `build/repo-all` | §6 |
| Stale meta | `system-minimal` 0.1-3 requires `NetworkManager`, `dhcp`, `finit`, `sysklogd`, `wpa-supplicant`; none is in the repo | `rpm -qpR build/repo-all/system-minimal-0.1-2.x86_64.rpm` shows the older build; spec still has them |
| Specs not in repo | 276 specs have no RPM in `build/repo-all`; 147 were last touched in 2019/2020, 3 in 2021, 123 in 2023, 3 in 2026 | `git log -1 --format=%cs` per spec |
| Retired specs | `atk`, `at-spi2-atk`, `check`, `dhcp`, `gtk-xfce-engine`, `libcroco`, `mandoc`, `python2`, `udev`, `xfce4-xkb-plugin` have current book pages only in `archive/` | plus the 5 duplicate/retired names in §3.2 |
| Retired by plan | The C7 removals are clean: no `browneye-basefs-nousr`, `browneye-init`, `libwnck2`, `lxterminal`, `python2-urlgrabber`, `sysvinit`, `valgrind`, `webkitgtk` or `yum` directory remains | directory check |
| Static filelists | 81 of 256 shipped specs do not use `%files -f`; 175 do. No missing/dangling filelist reference was found. The workstation/binary specs (`nodejs`, `rust`, `opencode-bin`, `herdr`, `xfce-desktop`, `system-minimal`) are in the inline group. | `%files` scan |
| Source tarball cache | `~/rpmbuild/SOURCES` is missing 35 source files referenced by shipped specs (mostly recent container-built packages). This is a cache gap, not necessarily a repo defect; the three version-mismatch cases above are the real reproducibility failures. | `SOURCES` existence check |

## 6. Spec vs repo drift

`build/repo-all` contains 282 RPMs produced from 256 source specs. Every RPM
maps back to a spec (no orphan RPM), but the following shipped specs have
moved past the RPM that is in the repo:

| spec | spec version-release | repo RPM | note |
|---|---|---|---|
| `linux-firmware` | 20261019-3 | 20261019-2 | firmware split/release bump not rebuilt into repo |
| `mesa` | 26.2.3-2 | 26.2.3-1 | release bump not rebuilt |
| `python` | 3.14.7-2 | 3.14.7-1 | Python split release |
| `system-minimal` | 0.1-3 | 0.1-2 | spec requires `linux-firmware-base`; RPM requires `linux-firmware` |
| `xfce-desktop` | 4.20-4 | 4.20-3 | spec requires `linux-firmware-base`; RPM requires `linux-firmware` |

The remaining 251 shipped source specs match the repo version-release. The
276 specs in §2 are not represented in the repo at all.

## 7. Newer than book

| package | local | book | status |
|---|---|---|---|
| `nodejs` | 26.13.0 | 26.9.0 | shipped; approved D17 (`/opt` binary) |
| `rust` | 1.99.0 | 1.98.1 | shipped; approved D31 (`/opt` binary) |
| `db` | 6.2.32 | 5.3.28 | spec-only, not built; genuine newer version |

`unzip` 60 vs book 6.0 and `zip` 30 vs book 3.0 are **not** newer versions;
they are the same releases written without the decimal point. The stock
audit reports them as `NEWER/SPEC-ONLY`.

`sqlite` 3.53.4 is also **not** newer. The stock audit turns the LFS
autoconf entity `3530400` into `3.53.0`; LFS also carries
`sqlite-short-version` = `3.53.4`, which is the real book version and equals
the spec.

## 8. Reconciliation with `scripts/audit_versions.py`

The stock script printed:

| stock status | count |
|---|---:|
| OK | 211 |
| OUTDATED/SPEC-ONLY | 109 |
| NO-BOOK | 68 |
| NO-BOOK/SPEC-ONLY | 151 |
| OK/SPEC-ONLY | 15 |
| NEWER | 3 |
| NEWER/SPEC-ONLY | 3 |
| **total rows** | **560** |

Reconciled view:

- **OUTDATED/SPEC-ONLY 109 → 154.** All 109 stock rows are valid; the
  script then misses **45** spec-only packages because it only applies
  aliases in the RPM branch, not the spec branch. The 45 are:
  `cairomm`, `dconf`, `font-ttf-unifont`, `fuse`, `gcr`, `gnupg`,
  `gsettings-desktop-schemas`, `gst-plugins-base`, `gstreamer`, `gtkmm`,
  `libglu`, `libopus`, `libpeas`, `libpoppler`, `libsecret`, `libx264`,
  `libx265`, `openjpeg`, `perl-io-sockets-ssl`, `perl-uri`, `python-mako`,
  `python-pycairo`, `python-pygobject`, `python-pyparsing`, `python-six`,
  `python-sphinx`, `python3-alabaster`, `python3-babel`,
  `python3-certifi`, `python3-chardet`, `python3-idna`,
  `python3-imagesize`, `python3-pygments`, `python3-pytz`,
  `python3-requests`, `python3-snowballstemmer`,
  `python3-sphinxcontrib-applehelp`, `-devhelp`, `-htmlhelp`, `-qthelp`,
  `-serializinghtml`, `python3-urllib3`, `webp`, `xf86-input-synaptics`,
  `xorriso`.
- **NO-BOOK/SPEC-ONLY 151 → 98 true no-book + 5 retired + 45 moved below +
  3 equal.** The 45 moved below are the list above. The 5 retired are
  `fuse2`, `libsoup`, `pcre`, `sdl`, `sqlite3`. The 3 equal are
  `docbook-xsl-nons` (alias of the book `docbook-xsl`), `liblzo2`
  (alias of book `lzo`) and `python3-sphinxcontrib-jsmath` (alias of
  `sc-jsmath`). No stock no-book row disappeared without a replacement.
- **NO-BOOK 68 → 27 real shipped no-book + 28 subpackages + 13 aliases.**
  The 28 subpackages are `clang*`, `compiler-rt`, `llvm-*`, `dbus-daemon`,
  `dbus-libs`, `dbus-x11`, `gcc-libs`, `gettext-*`, `glibc-*`,
  `openssl-*`, `linux-kernel`, `linux-modules`, `python3-rpm`. The 13
  aliases are `freetype`→`freetype2`, `gtk+`→`gtk3`, `icu4c`→`icu`,
  `libyaml`→`yaml`, `vte`→`vte`, `xf86-input-libinput`→
  `xorg-libinput-driver`, and the six `python-*` module specs plus
  `python3-docutils`. The 27 real ones are in §3.1.
- **OK 211 + NEWER 3 = 214 RPM rows.** The 214 differs from the 229
  book-matched source specs because the 28 subpackages are counted as
  separate NO-BOOK RPMs and because the stock script deduplicates by RPM
  `Name`. The stock `NEWER` 3 is `nodejs`, `rust`, `sqlite`; the first two
  are real, `sqlite` is the `3530400` parser artifact described in §7.
- **OK/SPEC-ONLY 15 + NEWER/SPEC-ONLY 3 = 18 audit rows; reconciled 16
  equal + 3 newer = 19.** The audit's 15 includes `dbus` and `linux`,
  which are actually shipped source packages whose main RPM name does not
  exist (they ship only subpackages), so they are not spec-only here. It
  misses `docbook-xsl-nons`, `liblzo2` and `python3-sphinxcontrib-jsmath`,
  which are aliases of current book entities and are equal. Net +1. The 3
  newer are `db` (real) plus `unzip`/`zip` (format artifacts).

Known parser gaps, independent of this report:

1. `NO-BOOK` is decided from the RPM `Name`, so every subpackage of a book
   source package becomes `NO-BOOK`.
2. The alias table is applied to RPMs only; spec-only names are looked up
   raw. `icu4c` vs `icu`, `libyaml` vs `yaml`, `gtk+` vs `gtk3`,
   `freetype` vs `freetype2`, `webp` vs `libwebp`, `xorriso` vs
   `libisoburn`, `python-*` vs the LFS module names, etc. are affected.
3. Entity names that encode a role rather than the package name are not
   mapped: `xorg-libinput-driver`, `xorg-synaptics-driver`,
   `xorg-vesa-driver`, `sc-applehelp` … `sc-serializinghtml`.
4. `gnome.ent` is not read, although it defines `vte-version` and other
   GNOME entity versions. `vte` therefore shows as NO-BOOK.
5. The `sqlite` special case truncates `3530400` to `3.53.0` and ignores
   `sqlite-short-version` = `3.53.4`.
6. `unzip` 60 and `zip` 30 are compared lexically with 6.0/3.0.
7. The script does not inspect `sources`, patches, `SourceN`, filelists,
   spec-vs-RPM drift, or `lfs.lock` staleness at all.

The `LVM2` / `libelf` / `procps` / `pcre` aliases the task mentions work
for shipped RPMs: `LVM2` normalises to `lvm2`, `libelf` is aliased to
`elfutils`, `procps` to `procps-ng`, and `pcre` to `pcre2`. They do not
help the *spec-only* `pcre` (PCRE1 8.42), which is a different package from
book `pcre2`; that spec is classified retired here, not outdated.

## 9. Reproduction

All commands are read-only. Run from the audit worktree (or the main tree).

```bash
# Stock audit (writes nothing)
cd ~/browneye-spec-audit
python3 scripts/audit_versions.py | head -40

# Shipped RPM set and source mapping
for f in build/repo-all/*.rpm; do
  rpm -qp --qf '%{NAME}\t%{VERSION}\t%{RELEASE}\t%{SOURCERPM}\n' "$f"
done | sort > /tmp/repo-all.tsv

# Specs vs repo drift (version 1: the five listed in §6)
for d in package_specs/*/; do
  n=$(basename "$d")
  spec=$(ls "$d"/*.spec 2>/dev/null | head -1)
  [ -n "$spec" ] || continue
  v=$(sed -n 's/^Version:[[:space:]]*//p' "$spec" | head -1)
  r=$(sed -n 's/^Release:[[:space:]]*//p' "$spec" | head -1)
  rpm=$(ls build/repo-all/"$n"-*.rpm 2>/dev/null | head -1)
  [ -n "$rpm" ] && echo "$n spec=$v-$r rpm=$(basename "$rpm")"
done

# Sources file vs spec version (inspect the reported mismatches)
grep -n . package_specs/{cpio,dracut,linux-firmware,autoconf,dnf-plugins-core,sqlite,fuse}/sources

# Missing sources / nosources markers
for d in package_specs/*/; do
  [ -f "$d/sources" ] || [ -f "$d/nosources" ] || echo "no source marker: $d"
done

# Patch references that are not in files/ or sources
grep -rn 'patch' package_specs/lua/lua.spec package_specs/coreutils/coreutils.spec

# lfs.lock vs trunk (the lock is tag r13.1)
git -C ~/repos/lfs log --oneline -1
python3 - <<'PY'
import json
d=json.load(open('lfs.lock'))
for n in ('man-pages','iana-etc','xz','pcre','pkgconf','expat','automake',
          'openssl','libelf','iproute2','vim','systemd'):
    print(n, d['packages'].get(d['canonical_names'].get(n,n)))
PY
```

## 10. Caveats

- This audit compares **versions**, not build recipes. A spec can be at the
  book version and still fail to build (see `lua` and the source-file
  mismatches).
- Book versions were read from the full current trunk entity set, including
  `gnome.ent` and the X driver pages, not just `packages.ent`. In a few
  places the book uses a role entity (`xorg-libinput-driver`,
  `sc-applehelp`, `libisoburn` for xorriso); the mapping to the spec name
  is stated in the relevant row.
- `pcre` 8.42 is PCRE1, not book `pcre2`; `libsoup` 2.62.3 is libsoup2, not
  book libsoup3. These are listed as retired, not as below-book versions.
- `fuse` 3.2.5 is compared with book `fuse3` 3.18.3, but its `sources` file
  actually points at 2.9.7 (the `fuse`/`fuse2` URL swap). Treat the
  below-book row as "spec metadata is internally inconsistent", not as a
  clean 3.2.5 build.
- `xf86-video-vesa` and `xf86-video-amdgpu`/`-intel`/`-fbdev`/`-vmware`
  are archive-only in the current book. They are NO-BOOK, not outdated.
- The `build/repo-all` tree is a 282-RPM staging tree; the last published
  tree was 258 RPMs. Git history records that the split waves are newer
  than the published tree. This audit treats `build/repo-all` as the
  shipped set, as instructed.
- `~/rpmbuild/SOURCES` was read only to check whether referenced files
  exist. A missing cached tarball is reported only when the `sources` file
  itself points at the wrong version; many recent container-built packages
  are simply absent from that host cache.
- The 2019/2020 spec dates come from `git log -1 --format=%cs`; they show
  when the spec file last changed, not when the package was last attempted.
- Counts for the book-matched set use source packages, not RPM names. A
  source package with subpackages counts once; the stock script counts
  RPM names and therefore double-counts the split packages.
