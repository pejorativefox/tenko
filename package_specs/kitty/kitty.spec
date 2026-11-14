Name:       kitty
Version:    0.50.0
Release:    1
Summary:    Fast, feature-rich, GPU based terminal emulator
License:    GPL-3.0-only AND Zlib AND MIT
URL:        https://sw.kovidgoyal.net/kitty/
Source0:    %{name}-%{version}.tar.xz
# Build only the X11 glfw backend: Tenko's desktop is X11/XFCE (issue #30).
# setup.py has no switch for this; under Wayland kitty runs on XWayland.
Patch0:     %{name}-%{version}-x11-only.patch
Prefix:     /usr
ExclusiveArch: x86_64

# Replaces the repackaged upstream binary bundle.
Provides:   kitty-bin = %{version}-%{release}
Obsoletes:  kitty-bin < 0.50.0

BuildRequires: python
BuildRequires: pkgconf
BuildRequires: harfbuzz
BuildRequires: freetype
BuildRequires: fontconfig
BuildRequires: libpng
BuildRequires: cairo
BuildRequires: lcms2
BuildRequires: xxhash
BuildRequires: simde
BuildRequires: openssl
BuildRequires: zlib
BuildRequires: mesa
BuildRequires: libx11
BuildRequires: libxcb
BuildRequires: libxkbcommon
BuildRequires: libxcursor
BuildRequires: libxrandr
BuildRequires: libxi
BuildRequires: libxinerama
BuildRequires: libxext
BuildRequires: libxrender
# The rest of the pkg-config chain the .pc files above pull in.
BuildRequires: xorgproto
BuildRequires: pixman
BuildRequires: libxau
BuildRequires: libXdmcp
BuildRequires: libxfixes
BuildRequires: libxxf86vm
BuildRequires: libdrm
BuildRequires: glib
BuildRequires: dbus-daemon
BuildRequires: dbus-libs
BuildRequires: ncurses
# kitten is a Go program; its modules are downloaded during the build and
# verified against go.sum.
BuildRequires: go
BuildRequires: make-ca
# slangc generates the shaders; the Symbols Nerd Font Mono face is copied
# into kitty's fonts directory (setup.py looks it up with fc-list).
BuildRequires: shader-slang
BuildRequires: font-nerd-symbols

# Loaded at runtime, so rpm cannot see them: Python runs kitty's code,
# libGL/libEGL and libxkbcommon-x11 are dlopened by glfw, and slangc
# compiles user custom shaders.
Requires:   python
Requires:   mesa
Requires:   libx11
Requires:   libxcursor
Requires:   dbus-libs
Requires:   fontconfig
Requires:   shader-slang
Requires:   hicolor-icon-theme

%description
kitty is a fast, feature-rich, GPU based terminal emulator with tabs and
split windows, true colour, ligatures, graphics and image display,
hyperlinks, shell integration, custom shaders and remote control, plus
the kitten helper for ssh, file transfer, icat, diff and more.

Built from source against the system Python and libraries, with the X11
backend only.  Updates come from the Tenko repository, so the upstream
update check is off.

%prep
%setup -q
%patch -P 0 -p1

%build
export GOPATH="$PWD/.gopath" GOFLAGS=-modcacherw GOTOOLCHAIN=local
python3 setup.py linux-package \
    --prefix="$PWD/linux-package" \
    --libdir-name=lib64 \
    --update-check-interval=0 \
    --verbose

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_prefix}
cp -a linux-package/. %{buildroot}%{_prefix}/
install -Dm644 LICENSE %{buildroot}%{_licensedir}/kitty/LICENSE

%check
pkg=$PWD/linux-package
"$pkg/bin/kitty" --version
"$pkg/bin/kitten" --version
# X11 backend built, Wayland backend not; the C core and its libraries load.
test -e "$pkg/lib64/kitty/kitty/glfw-x11.so"
test ! -e "$pkg/lib64/kitty/kitty/glfw-wayland.so"
"$pkg/bin/kitty" +runpy 'import kitty.fast_data_types, kittens.transfer.rsync; print("modules ok")'
test -s "$pkg/lib64/kitty/fonts/SymbolsNerdFontMono-Regular.ttf"
test -s "$pkg/lib64/kitty/shaders/cell.spv"

%files -f %{_sourcedir}/kitty.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 0.50.0-1
- New package built from source, replacing the repackaged upstream bundle
  (kitty-bin 0.49.2; Provides/Obsoletes kitty-bin).  0.50.0 is the latest
  upstream stable release (2026-11-03, checked 2026-11-14).  Not in the
  base set.  Issue #30.
- X11 glfw backend only (patched in setup.py); upstream update check off.
- Uses the system Python, harfbuzz, freetype, fontconfig, lcms2, xxhash,
  OpenSSL and libpng; shaders generated with shader-slang, which is also
  required at runtime for custom shaders.  Installed under /usr with the
  Python package and data in /usr/lib64/kitty.
