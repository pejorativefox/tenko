Name:       garcon
Version:    4.20.0
Release:    3
Summary:    Implementation of the freedesktop.org menu specification
License:    LGPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: libxfce4ui

%description
Implementation of the freedesktop.org menu specification

%package doc
Summary:    garcon documentation
Requires:   garcon = %{version}-%{release}

%description doc
Documentation for garcon.

%package devel
Summary:    garcon development files
Requires:   %{name}-gir = %{version}-%{release}
Requires:   garcon = %{version}-%{release}

%description devel
Development files for garcon.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install


%package gir
Summary:    GObject Introspection data for garcon
License:    LGPL
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for garcon, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the -devel package.

%files -f %{_sourcedir}/garcon.filelist
%files doc -f %{_sourcedir}/garcon-doc.filelist
%files devel -f %{_sourcedir}/garcon-devel.filelist
%files gir -f %{_sourcedir}/garcon-gir.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20.0-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.0-2
- Split doc, devel payload into garcon-doc, garcon-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with BLFS r13.1 (4.19.0)

* Wed Aug 30 2023  Chris Statzer <chris.statzer@gmail.com> 4.19.0

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.6.4
- Initial RPM

