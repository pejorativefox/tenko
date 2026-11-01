Name:       libxklavier
Version:    5.4
Release:    2
Summary:    High-level API for X Keyboard Extension
License:    LGPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
High-level API for X Keyboard Extension

%package devel
Summary:    libxklavier development files
Requires:   libxklavier = %{version}-%{release}

%description devel
Development files for libxklavier.

%package static
Summary:    libxklavier static libraries
Requires:   libxklavier = %{version}-%{release}

%description static
Static libraries for libxklavier.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libxklavier.filelist
%files devel -f %{_sourcedir}/libxklavier-devel.filelist
%files static -f %{_sourcedir}/libxklavier-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 5.4-2
- Split devel, static payload into libxklavier-devel, libxklavier-static (size audit)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 5.4
- Initial RPM

