Name:       xfconf
Version:    4.20.0
Release:    3
Summary:    Flexible, easy-to-use configuration management system
License:    GPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Flexible, easy-to-use configuration management system

%package lang
Summary:    xfconf translations
Requires:   xfconf = %{version}-%{release}

%description lang
Translations for xfconf.

%package doc
Summary:    xfconf documentation
Requires:   xfconf = %{version}-%{release}

%description doc
Documentation for xfconf.

%package devel
Summary:    xfconf development files
Requires:   %{name}-gir = %{version}-%{release}
Requires:   xfconf = %{version}-%{release}

%description devel
Development files for xfconf.

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
Summary:    GObject Introspection data for xfconf
License:    GPL
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for xfconf, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the -devel package.

%files -f %{_sourcedir}/xfconf.filelist
%files lang -f %{_sourcedir}/xfconf-lang.filelist
%files doc -f %{_sourcedir}/xfconf-doc.filelist
%files devel -f %{_sourcedir}/xfconf-devel.filelist
%files gir -f %{_sourcedir}/xfconf-gir.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20.0-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.0-2
- Split lang, doc, devel payload into xfconf-lang, xfconf-doc, xfconf-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with BLFS r13.1 (4.19.0)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.1
- Initial RPM

