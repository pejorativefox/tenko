Name:       libxfce4ui
Version:    4.20.2
Release:    3
Summary:    Commonly used Xfce widgets among Xfce applications
License:    GPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: xfconf

%description
Commonly used Xfce widgets among Xfce applications

%package lang
Summary:    libxfce4ui translations
Requires:   libxfce4ui = %{version}-%{release}

%description lang
Translations for libxfce4ui.

%package doc
Summary:    libxfce4ui documentation
Requires:   libxfce4ui = %{version}-%{release}

%description doc
Documentation for libxfce4ui.

%package devel
Summary:    libxfce4ui development files
Requires:   %{name}-gir = %{version}-%{release}
Requires:   libxfce4ui = %{version}-%{release}

%description devel
Development files for libxfce4ui.

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
Summary:    GObject Introspection data for libxfce4ui
License:    GPL
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for libxfce4ui, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the -devel package.

%files -f %{_sourcedir}/libxfce4ui.filelist
%files lang -f %{_sourcedir}/libxfce4ui-lang.filelist
%files doc -f %{_sourcedir}/libxfce4ui-doc.filelist
%files devel -f %{_sourcedir}/libxfce4ui-devel.filelist
%files gir -f %{_sourcedir}/libxfce4ui-gir.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20.2-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.2-2
- Split lang, doc, devel payload into libxfce4ui-lang, libxfce4ui-doc, libxfce4ui-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.2
- Sync with BLFS r13.1 (4.19.2)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.2
- Version Bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.1
- Initial RPM

