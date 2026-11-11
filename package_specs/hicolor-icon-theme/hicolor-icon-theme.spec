Name:       hicolor-icon-theme
Version:    0.18
Release:    2
Summary:    Gnome hicolor icon theme.
License:    GPL-2.0-only
URL:        https://gitlab.freedesktop.org/xdg/default-icon-theme
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Gnome hicolor icon theme

%prep
%setup

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/hicolor-icon-theme.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.18-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-only): COPYING (issue #8).

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.17
- Initial RPM

