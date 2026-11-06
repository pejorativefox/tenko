Name:       libsm
Version:    1.2.6
Release:    4
Summary:    X Session Management Library
License:    MIT AND MIT-open-group
Prefix:     /usr
Source0:    libSM-1.2.6.tar.xz

BuildRequires: libice

%description
X Session Management Library

%package doc
Summary:    libsm documentation
Requires:   libsm = %{version}-%{release}

%description doc
Documentation for libsm.

%package static
Summary:    libsm static libraries
Requires:   libsm = %{version}-%{release}

%description static
Static libraries for libsm.

%prep
%setup -q -n libSM-%{version}

%build
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libsm.filelist
%files doc -f %{_sourcedir}/libsm-doc.filelist
%files static -f %{_sourcedir}/libsm-static.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.6-4
- Record the verified license (MIT AND MIT-open-group): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.6-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.6-2
- Split doc, static, devel payload into libsm-doc, libsm-static, libsm-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.2.6
- Sync with 1.2.4

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.4-1
- Version bump
