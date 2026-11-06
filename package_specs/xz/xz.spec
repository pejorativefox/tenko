Name:       xz
Version:    5.8.4
Release:    4
Summary:    Free general-purpose data compression software
License:    0BSD AND LGPL-2.1-or-later AND GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
XZ Utils is free general-purpose data compression software with a high compression ratio. 

%package lang
Summary:    xz translations
Requires:   xz = %{version}-%{release}

%description lang
Translations for xz.

%package doc
Summary:    xz documentation
Requires:   xz = %{version}-%{release}

%description doc
Documentation for xz.

%prep
%setup -q

%build
./configure --prefix=/usr    \
            --disable-static \
            --docdir=/usr/share/doc/xz-%{version} \
            --libdir=%{_libdir}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xz.filelist
%files lang -f %{_sourcedir}/xz-lang.filelist
%files doc -f %{_sourcedir}/xz-doc.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.8.4-4
- Record the verified license (0BSD AND LGPL-2.1-or-later AND GPL-2.0-or-later): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.8.4-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 5.8.4-2
- Split lang, doc, devel payload into xz-lang, xz-doc, xz-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 5.8.3
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 5.8.3
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 5.4.4
- Version bump
