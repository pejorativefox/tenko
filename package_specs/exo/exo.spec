Name:       exo
Version:    4.20.0
Release:    2
Summary:    Application library for Xfce
License:    GPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Application library for Xfce

%package lang
Summary:    exo translations
Requires:   exo = %{version}-%{release}

%description lang
Translations for exo.

%package doc
Summary:    exo documentation
Requires:   exo = %{version}-%{release}

%description doc
Documentation for exo.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/exo.filelist
%files lang -f %{_sourcedir}/exo-lang.filelist
%files doc -f %{_sourcedir}/exo-doc.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.0-2
- Split lang, doc payload into exo-lang, exo-doc (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with BLFS r13.1 (4.18.0)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.18.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.12.8
- Initial RPM

