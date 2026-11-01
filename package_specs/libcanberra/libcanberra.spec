Name:       libcanberra
Version:    0.30
Release:    2
Summary:    libcanberra is an implementation of the XDG Sound Theme and Name Specifications
License:    GPL
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
libcanberra is an implementation of the XDG Sound Theme and Name Specifications

%package devel
Summary:    libcanberra development files
Requires:   libcanberra = %{version}-%{release}

%description devel
Development files for libcanberra.

%prep
%setup

%build
%configure --disable-oss
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libcanberra.filelist
%files devel -f %{_sourcedir}/libcanberra-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.30-2
- Split devel payload into libcanberra-devel (size audit)

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 0.30
- Initial RPM

