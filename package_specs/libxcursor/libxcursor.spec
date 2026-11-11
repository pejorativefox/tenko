Name:       libxcursor
Version:    1.2.3
Release:    4
Summary:    Xlib-based Cursor management library
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxcursor
Prefix:     /usr
Source0:    libXcursor-%{version}.tar.xz
BuildRequires: libxrender
BuildRequires: libx11
BuildRequires: libxfixes
BuildRequires: util-macros
BuildRequires: xorgproto

%description
Xlib-based Cursor management library

%package static
Summary:    libxcursor static libraries
Requires:   libxcursor = %{version}-%{release}

%description static
Static libraries for libxcursor.

%prep
%setup -q -n libXcursor-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxcursor.filelist
%files static -f %{_sourcedir}/libxcursor-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.3-4
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.3-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.3-2
- Split devel, static payload into libxcursor-devel, libxcursor-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.2.3
- Sync with 1.2.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.1-1
- Version bump
