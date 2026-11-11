Name:       xauth
Version:    1.1.5
Release:    1
Summary:    X authority file utility
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xauth
Prefix:     /usr
Source0:    xauth-1.1.5.tar.xz

%description
xauth manages the X authorization files used by Xorg.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xauth.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.5-1
- Initial package
