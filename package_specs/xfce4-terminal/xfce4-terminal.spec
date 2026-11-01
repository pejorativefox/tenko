Name:       xfce4-terminal
Version:    1.2.0
Release:    1
Summary:    Xfce terminal emulator
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: libxfce4ui
BuildRequires: vte
Requires:   libxfce4ui
Requires:   vte

%description
Xfce4 Terminal is a GTK+3 terminal emulator for the Xfce desktop.

%prep
%setup -q
# BLFS workaround: guard functions that are only available with
# gtk-layer-shell, which is not part of BLFS.
sed -e '570i #ifdef HAVE_GTK_LAYER_SHELL' \
    -e '574a #endif'                      \
    -i terminal/terminal-window-dropdown.c

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -Ddoc=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/xfce4-terminal.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.0
- Initial RPM, synced with BLFS r13.1 (xfce4-terminal 1.2.0)
- Build with -Ddoc=false: the man page needs docbook-xsl-nons, which is
  not installed in the build image; the terminal itself is unaffected
