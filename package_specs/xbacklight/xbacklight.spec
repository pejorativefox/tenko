Name:       xbacklight
Version:    1.2.4
Release:    1
Summary:    Adjust backlight brightness using RandR extension
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xbacklight
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: libxcb
BuildRequires: util-macros
BuildRequires: xcb-util

%description
xbacklight is a simple command-line client to adjust the backlight
brightness of a display using the X RandR extension.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xbacklight.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.4-1
- Update to 1.2.4 (latest upstream release)
- Not in the base set; version taken from
  upstream x.org
- Fix man page path in %files (/usr/share/man, not /usr/man)
