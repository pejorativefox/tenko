Name:       expat
Version:    2.9.0
Release:    3
Summary:    stream-oriented XML parser
License:    MIT
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
stream-oriented XML parser

%prep
%setup -q

%build
%configure --disable-static \
           --docdir=/usr/share/doc/expat-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/expat.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.9.0-3
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.9.0-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 2.9.0-1
- Update to 2.9.0 (current LFS/BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.8.4-2
- Split devel payload into expat-devel (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.8.3
- Sync with LFS r13.1

# let's skip this for now
