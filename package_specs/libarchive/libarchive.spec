Name:       libarchive
Version:    3.8.11
Release:    4
Summary:    Library for various archive formats
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The libarchive library provides a single interface for reading/writing various compression formats. 

%package static
Summary:    libarchive static libraries
Requires:   libarchive = %{version}-%{release}

%description static
Static libraries for libarchive.

%package devel
Summary:    Development files for libarchive
Requires:   %{name} = %{version}-%{release}

%description devel
pkg-config files for libarchive, used to build software against it.

%prep
%setup -q

%build
%configure --without-xml2
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libarchive.filelist
%files devel -f %{_sourcedir}/libarchive-devel.filelist
%files static -f %{_sourcedir}/libarchive-static.filelist


%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 3.8.11-4
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.8.11-2
- Move the pkg-config files into a new -devel subpackage so the runtime
  package no longer drags pkgconfig(...) consumers into every install.

* Mon Nov  2 2026 browneye <build@browneye.invalid> 3.8.11-1
- Update to 3.8.11 (current LFS/BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.8.9-3
- Split static payload into libarchive-static (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.8.9-2
- Build without libxml2/xar support (size audit P0); rpm/tar do not need it

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 3.7.1-1
- Version bump
