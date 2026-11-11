Name:       libxft
Version:    2.3.9
Release:    4
Summary:    Xorg font rendering library
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxft
Prefix:     /usr
Source0:    libXft-%{version}.tar.xz
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: libx11
BuildRequires: libxrender
BuildRequires: util-macros
BuildRequires: xorgproto
%description
Client side font rendering library, using libfreetype, libX11, and the X Render extension to display anti-aliased text.

%package static
Summary:    libxft static libraries
Requires:   libxft = %{version}-%{release}

%description static
Static libraries for libxft.

%prep
%setup -q -n libXft-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxft.filelist
%files static -f %{_sourcedir}/libxft-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.3.9-4
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.3.9-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.3.9-2
- Split devel, static payload into libxft-devel, libxft-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.3.9
- Sync with 2.3.8

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2.3.8-1
- Version bump
