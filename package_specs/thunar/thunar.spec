Name:       thunar
Version:    4.20.10
Release:    3
Summary:    Modern file manager for Xfce
License:    GPL2
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Modern file manager for Xfce

%package lang
Summary:    thunar translations
Requires:   thunar = %{version}-%{release}

%description lang
Translations for thunar.

%package doc
Summary:    thunar documentation
Requires:   thunar = %{version}-%{release}

%description doc
Documentation for thunar.

%package devel
Summary:    thunar development files
Requires:   %{name}-gir = %{version}-%{release}
Requires:   thunar = %{version}-%{release}

%description devel
Development files for thunar.

%prep
%setup 

%build
sed -i 's/\tinstall-systemd_userDATA/\t/' Makefile.in
%configure --docdir=/usr/share/doc/thunar-%{version}
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install


%package gir
Summary:    GObject Introspection data for thunar
License:    GPL2
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for thunar, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the -devel package.

%files -f %{_sourcedir}/thunar.filelist
%files lang -f %{_sourcedir}/thunar-lang.filelist
%files doc -f %{_sourcedir}/thunar-doc.filelist
%files devel -f %{_sourcedir}/thunar-devel.filelist
%files gir -f %{_sourcedir}/thunar-gir.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20.10-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.10-2
- Split lang, doc, devel payload into thunar-lang, thunar-doc, thunar-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.9
- Sync with BLFS r13.1 (4.18.6)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.18.6
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.8.9
- Initial RPM

