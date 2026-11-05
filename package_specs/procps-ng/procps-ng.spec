Name:       procps-ng
Version:    4.0.7
Release:    3
Summary:    Process monitoring utilities
License:    GPL3
Source0:    procps-ng-%{version}.tar.xz
Prefix:     /usr

%description
The Procps-ng package contains programs for monitoring processes. 

%package lang
Summary:    procps-ng translations
Requires:   procps-ng = %{version}-%{release}

%description lang
Translations for procps-ng.

%package doc
Summary:    procps-ng documentation
Requires:   procps-ng = %{version}-%{release}

%description doc
Documentation for procps-ng.

%prep
%setup -q 

%build
%configure  --docdir=/usr/share/doc/procps-ng-%{version} \
            --disable-static                         \
            --disable-kill

%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/procps-ng.filelist
%files lang -f %{_sourcedir}/procps-ng-lang.filelist
%files doc -f %{_sourcedir}/procps-ng-doc.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.0.7-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.0.7-2
- Split lang, doc, devel payload into procps-ng-lang, procps-ng-doc, procps-ng-devel (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.0.7
- Sync with LFS r13.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 4.0.3-1
- Version bump
