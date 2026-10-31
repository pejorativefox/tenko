Name:       libxfce4ui
Version:    4.20.2
Release:    1
Summary:    Commonly used Xfce widgets among Xfce applications
License:    GPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: xfconf

%description
Commonly used Xfce widgets among Xfce applications

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/share/
/usr/include/xfce4/
/usr/bin/xfce4-about
/usr/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml
/usr/lib64/

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.2
- Sync with BLFS r13.1 (4.19.2)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.2
- Version Bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.1
- Initial RPM

