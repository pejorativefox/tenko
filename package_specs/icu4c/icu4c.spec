Name:       icu4c
Version:    78.3
Release:    2
Summary:    International Components for Unicode (C/C++ libraries)
License:    Unicode-3.0
URL:        https://icu.unicode.org/
Source0:    %{name}-%{version}-sources.tgz
Prefix:     /usr

%description
ICU is a mature, widely used set of C/C++ libraries providing Unicode and
globalization support for software applications.  This package provides the
icu4c libraries and tools.

%package devel
Summary:    icu4c development files
Requires:   icu4c = %{version}-%{release}

%description devel
Development files for icu4c.

%prep
%setup -q -n icu

%build
pushd source
%configure
%make_build
popd

%install
rm -rf %{buildroot}
pushd source
%make_install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/icu4c.filelist
%files devel -f %{_sourcedir}/icu4c-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 78.3-2
- Split devel payload into icu4c-devel (size audit)

* Sun Nov 01 2026 Browneye Node.js wave <daspork@browneye.invalid> 78.3-1
- Update 73.2 -> 78.3 (BLFS r13.1 packages.ent icu-version 78.3).
  The spec directory and RPM name stay icu4c; BLFS calls the package "icu".
- Source: https://github.com/unicode-org/icu/releases/download/release-78.3/icu4c-78.3-sources.tgz
  md5 a7b736b570ef0e180c96a31715a00c78
  sha256 3a2e7a47604ba702f345878308e6fefeca612ee895cf4a5f222e7955fabfe0c0
- Configure: ./configure --prefix=/usr (from source/, BLFS r13.1).
- Static filelist generated from the install tree (sonames are now .78).
- Consumers of libicu*.so.73 must be rebuilt against this ABI.
