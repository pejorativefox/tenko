Name:       libarchive
Version:    3.8.11
Release:    1
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
%files static -f %{_sourcedir}/libarchive-static.filelist


%changelog
* Mon Nov  2 2026 browneye <build@browneye.invalid> 3.8.11-1
- Update to 3.8.11 (current LFS/BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.8.9-3
- Split static payload into libarchive-static (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.8.9-2
- Build without libxml2/xar support (size audit P0); rpm/tar do not need it

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 3.7.1-1
- Version bump
