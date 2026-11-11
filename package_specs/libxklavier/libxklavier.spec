Name:       libxklavier
Version:    5.4
Release:    5
Summary:    High-level API for X Keyboard Extension
License:    LGPL-2.0-or-later
URL:        https://gitlab.freedesktop.org/archived-projects/libxklavier
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr
BuildRequires: libx11
BuildRequires: libxi
BuildRequires: libxkbfile
BuildRequires: xorgproto
BuildRequires: libXdmcp
BuildRequires: libxau
BuildRequires: libxcb
BuildRequires: libxext
BuildRequires: libxfixes

%description
High-level API for X Keyboard Extension

%package static
Summary:    libxklavier static libraries
Requires:   libxklavier = %{version}-%{release}

%description static
Static libraries for libxklavier.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%package gir
Summary:    GObject Introspection data for libxklavier
License:    LGPL-2.0-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for libxklavier, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/libxklavier.filelist
%files static -f %{_sourcedir}/libxklavier-static.filelist
%files gir -f %{_sourcedir}/libxklavier-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.4-5
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.0-or-later): COPYING.LIB, GNU Library GPL v2, plus libxklavier/xklavier.c (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.4-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 5.4-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 5.4-2
- Split devel, static payload into libxklavier-devel, libxklavier-static (size audit)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 5.4
- Initial RPM

