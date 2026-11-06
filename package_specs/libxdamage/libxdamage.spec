Name:       libxdamage
Version:    1.1.7
Release:    4
Summary:    X Damage Extension library
License:    MIT
Prefix:     /usr
Source0:    libXdamage-%{version}.tar.xz
%description
X Damage Extension library

%package static
Summary:    libxdamage static libraries
Requires:   libxdamage = %{version}-%{release}

%description static
Static libraries for libxdamage.

%prep
%setup -q -n libXdamage-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxdamage.filelist
%files static -f %{_sourcedir}/libxdamage-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.7-4
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.7-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.7-2
- Split devel, static payload into libxdamage-devel, libxdamage-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.1.7
- Sync with 1.1.6

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.6-1
- Version bump
