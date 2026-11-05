Name:       libxres
Version:    1.2.3
Release:    4
Summary:    X-Resource extension client library
License:    MIT
Prefix:     /usr
Source0:    libXres-1.2.3.tar.xz

%description
X-Resource extension client library

%package static
Summary:    libxres static libraries
Requires:   libxres = %{version}-%{release}

%description static
Static libraries for libxres.

%prep
%setup -q -n libXres-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxres.filelist
%files static -f %{_sourcedir}/libxres-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.3-4
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.3-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.3-2
- Split devel, static payload into libxres-devel, libxres-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.2.3
- Sync with BLFS r13.1 (1.2.2)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.2-1
- Version bump
