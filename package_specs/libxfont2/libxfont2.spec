Name:       libxfont2
Version:    2.0.9
Release:    4
Summary:    X font handling library for server & utilities.
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxfont
Prefix:     /usr
Source0:    libXfont2-%{version}.tar.xz

BuildRequires: libfontenc
BuildRequires: freetype
BuildRequires: util-macros

%description
X font handling library for server & utilities.

%package static
Summary:    libxfont2 static libraries
Requires:   libxfont2 = %{version}-%{release}

%description static
Static libraries for libxfont2.

%prep
%setup -q -n libXfont2-%{version}

%build
%configure --disable-devel-docs
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxfont2.filelist
%files static -f %{_sourcedir}/libxfont2-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.0.9-4
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.0.9-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.0.9-2
- Split devel, static payload into libxfont2-devel, libxfont2-static (size audit)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2.0.6-1
- Version bump
