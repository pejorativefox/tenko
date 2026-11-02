Name:       libxklavier
Version:    5.4
Release:    3
Summary:    High-level API for X Keyboard Extension
License:    LGPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
High-level API for X Keyboard Extension

%package devel
Summary:    libxklavier development files
Requires:   %{name}-gir = %{version}-%{release}
Requires:   libxklavier = %{version}-%{release}

%description devel
Development files for libxklavier.

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
License:    LGPL
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for libxklavier, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the -devel package.

%files -f %{_sourcedir}/libxklavier.filelist
%files devel -f %{_sourcedir}/libxklavier-devel.filelist
%files static -f %{_sourcedir}/libxklavier-static.filelist
%files gir -f %{_sourcedir}/libxklavier-gir.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 5.4-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 5.4-2
- Split devel, static payload into libxklavier-devel, libxklavier-static (size audit)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 5.4
- Initial RPM

