Name:       screen
Version:    5.0.2
Release:    2
Summary:    Screen is a full-screen window manager that multiplexes a physical terminal between several processes
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Screen is a full-screen window manager that multiplexes a physical terminal between several processes

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -rf %{buildroot}/usr/share/info/dir

%files -f %{_sourcedir}/screen.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.0.2-2
- Record the verified license (GPL-3.0-or-later): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 5.0.2-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.8.0
- Initial RPM

