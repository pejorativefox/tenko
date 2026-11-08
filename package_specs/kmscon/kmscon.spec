# kmscon is a userspace KMS/DRM virtual console.  It replaces the in-kernel
# fbcon VT for tty1-6, which is what finally gives the console full UTF-8
# support: fbcon caps a font at 512 glyphs and therefore cannot draw Chinese.
# Built with the DRM 2D backend and the freetype/psf/unifont font modules; the
# OpenGL renderer and Pango backend are disabled to keep mesa and pango off
# the base dependency chain.
Name:       kmscon
Version:    10.1.1
Release:    3
Summary:    KMS/DRM userspace virtual console with full UTF-8 support
License:    MIT AND OFL-1.1
URL:        https://github.com/kmscon/kmscon
Prefix:     /usr
Source0:    kmscon-%{version}.tar.gz

BuildRequires: meson
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: gcc
BuildRequires: python
BuildRequires: systemd
BuildRequires: libdrm
BuildRequires: libxkbcommon
BuildRequires: libtsm
BuildRequires: freetype
BuildRequires: fontconfig
BuildRequires: zlib
BuildRequires: ncurses

Requires:   fontconfig
Requires:   freetype
Requires:   libdrm
Requires:   libxkbcommon
Requires:   libtsm
Requires:   zlib
Requires:   systemd
# kmscon reads the XKB layouts and keymaps from the system xkeyboard-config
# tree; without it the console keymap fallback is useless.
Requires:   xkeyboard-config
# The "Tenko Console" fontconfig family is Noto Sans Mono CJK SC with the
# monochrome emoji and Nerd Font symbol faces as fallbacks.  Install them with
# the console so a failure to resolve the family cannot leave a blank VT.
Requires:   font-noto-cjk
Requires:   font-noto-emoji
Requires:   font-nerd-symbols

%description
kmscon is a userspace terminal emulator for the Linux KMS/DRM console.  It
replaces the in-kernel fbcon virtual terminal and renders text with freetype
and fontconfig, so it supports the full Unicode repertoire that a userspace
font can cover, including Simplified Chinese and emoji.

The package is configured with the DRM 2D backend plus the freetype, PSF and
built-in GNU Unifont font backends.  A fontconfig alias named "Tenko Console"
selects Noto Sans Mono CJK SC and appends the monochrome Noto Emoji and Nerd
Fonts symbol faces, so a Chinese Wi-Fi SSID in nmtui and Nerd Font icons in a
shell prompt render on Ctrl+Alt+F2 instead of tofu.

Tenko enables kmscon on tty1 for new installs and switches an existing system
over in the package scriptlet.  The systemd unit keeps getty as an OnFailure
fallback, and lightdm/tenko-installer declare a conflict so the graphical
session or the live installer can take tty1 when they need it.

%prep
%setup -q

%build
mkdir -p build
pushd build
meson setup .. --prefix=%{_prefix} --buildtype=release \
    -Ddocs=disabled -Dtests=false -Dlibseat=disabled -Ddbus=disabled \
    -Dvideo_fbdev=disabled -Dvideo_drm2d=enabled -Dvideo_drm3d=disabled \
    -Drenderer_gltex=disabled \
    -Dfont_freetype=enabled -Dfont_pango=disabled \
    -Dfont_unifont=enabled -Dfont_psf=enabled
ninja
popd

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install
# The upstream unit skips itself when /dev/tty0 is absent at the time the
# condition is checked.  On an initramfs-less boot devtmpfs can create the
# node after getty.target has already pulled the unit, so the console is then
# skipped for the whole boot.  Tenko builds CONFIG_VT=y; drop the condition
# and rely on OnFailure=getty@%i.service if a VT is genuinely unavailable.
sed -i '/^ConditionPathExists=\/dev\/tty0$/d' \
    %{buildroot}%{_unitdir}/kmsconvt@.service
install -D -m 0644 %{_sourcedir}/69-tenko-console.conf \
    %{buildroot}%{_sysconfdir}/fonts/conf.d/69-tenko-console.conf
install -D -m 0644 %{_sourcedir}/kmscon.conf \
    %{buildroot}%{_sysconfdir}/kmscon/kmscon.conf
install -D -m 0644 %{_sourcedir}/50-tenko-console.preset \
    %{buildroot}%{_prefix}/lib/systemd/system-preset/50-tenko-console.preset

%post
# Preset-all runs during image assembly, but a plain dnf upgrade does not.
# Switch the live system over explicitly.  Disable the getty template (the
# instance disable alone leaves the autovt@.service alias pointing at getty)
# and the non-VT kmscon.service before enabling the VT instance.
if [ -x /usr/bin/systemctl ]; then
    /usr/bin/systemctl --root=/ disable getty@.service >/dev/null 2>&1 || :
    /usr/bin/systemctl --root=/ disable kmscon.service >/dev/null 2>&1 || :
    /usr/bin/systemctl --root=/ enable kmsconvt@tty1.service >/dev/null 2>&1 || :
fi

%files -f %{_sourcedir}/kmscon.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 10.1.1-3
- Remove the upstream ConditionPathExists=/dev/tty0 from kmsconvt@.service.
  On an initramfs-less boot the condition is evaluated before devtmpfs
  creates the node and the console is then skipped for the whole boot; the
  OnFailure=getty fallback still covers a system without a VT.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 10.1.1-2
- Clear the upstream ConditionPathExists=/dev/tty0 on kmsconvt@ with a
  drop-in.  On an initramfs-less boot the condition is evaluated before
  devtmpfs creates /dev/tty0 and the console is then skipped for the whole
  boot; the OnFailure=getty fallback still covers a system without a VT.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 10.1.1
- Package kmscon 10.1.1 (latest stable upstream release) with the DRM 2D,
  freetype, PSF and Unifont backends, the Tenko Console fontconfig alias and
  the tty1 activation preset.  This replaces fbcon on tty1-6, which is the
  only way to render Simplified Chinese in the text console: the kernel VT
  is capped at 512 glyphs.  OpenGL and Pango are disabled to keep mesa and
  pango out of the base dependency chain.
