Name:       exo
Version:    4.20.0
Release:    4
Summary:    Application library for Xfce
License:    GPL-2.0-or-later AND LGPL-2.0-or-later
URL:        https://docs.xfce.org/xfce/exo/start
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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.0-4
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND LGPL-2.0-or-later): COPYING, COPYING.LIB, exo-open/main.c and exo/exo-string.c (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.0-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.0-2
- Split lang, doc, devel payload into exo-lang, exo-doc, exo-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with 4.18.0

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.18.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.12.8
- Initial RPM

