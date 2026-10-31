Name:       libxklavier
Version:    5.4
Release:    1
Summary:    High-level API for X Keyboard Extension
License:    LGPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
High-level API for X Keyboard Extension

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libxklavier.filelist

%changelog
* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 5.4
- Initial RPM

