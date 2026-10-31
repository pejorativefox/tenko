Name:       garcon
Version:    4.20.0
Release:    1
Summary:    Implementation of the freedesktop.org menu specification
License:    LGPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: libxfce4ui

%description
Implementation of the freedesktop.org menu specification

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/etc/xdg/menus/xfce-applications.menu
/usr/include/garcon-1/garcon/
/usr/include/garcon-gtk3-1/garcon-gtk/
/usr/lib64/
/usr/share/

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with BLFS r13.1 (4.19.0)

* Wed Aug 30 2023  Chris Statzer <chris.statzer@gmail.com> 4.19.0

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.6.4
- Initial RPM

