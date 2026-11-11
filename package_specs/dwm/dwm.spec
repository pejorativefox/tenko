Name:       dwm
Version:    6.5
Release:    1
Summary:    Dynamic window manager for X
License:    MIT
URL:        https://dwm.suckless.org/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: gcc, make
BuildRequires: libx11, libxinerama, fontconfig, freetype
BuildRequires: libxft
BuildRequires: harfbuzz
BuildRequires: libXdmcp
BuildRequires: libpng
BuildRequires: libxau
BuildRequires: libxcb
BuildRequires: libxext
BuildRequires: libxrender
BuildRequires: xorgproto

%description
dwm is a dynamic window manager for X.  It manages windows in tiled,
monocle and floating layouts, and all of the layouts can be applied
dynamically.  This package is built with the default upstream config.h.

%prep
%setup -q

%build
%make_build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} PREFIX=/usr MANPREFIX=/usr/share/man

%files -f %{_sourcedir}/dwm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 6.5-1
- Not in the base set; latest upstream stable 2026-11-05
  (6.5).  Built with the default upstream config.h against libX11,
  libXinerama, fontconfig and freetype.
- Update from 6.2 to 6.5; install the dwm(1) man page as well.
