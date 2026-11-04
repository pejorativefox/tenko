Name:       tumbler
Version:    4.20.2
Release:    2
Summary:    D-Bus service for applications to request thumbnails
License:    GPL2
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
D-Bus service for applications to request thumbnails

%package devel
Summary:    tumbler development files
Requires:   tumbler = %{version}-%{release}

%description devel
Development files for tumbler.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
rm -f %{buildroot}/usr/lib/systemd/user/tumblerd.service

%files -f %{_sourcedir}/tumbler.filelist
%files devel -f %{_sourcedir}/tumbler-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.2-2
- Split devel payload into tumbler-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.2
- Sync with BLFS r13.1 (4.19.0)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.2.7
- Initial RPM

