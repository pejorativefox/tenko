Name:       xf86-input-synaptics
Version:    1.10.0
Release:    1
Summary:    Synaptics touchpad driver
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/driver/xf86-input-synaptics
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Synaptics touchpad driver

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/xf86-input-synaptics.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.10.0-1
- Update to xf86-input-synaptics 1.10.0. Not in the base set
  (x.org archive-era tool); latest upstream stable 2026-11-05.
* Mon May 18 2020 Chris Statzer <chris.statzer@qq.com> 1.9.1
- Initial RPM
