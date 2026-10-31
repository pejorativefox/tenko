Name:       hicolor-icon-theme
Version:    0.18
Release:    1
Summary:    Gnome hicolor icon theme.
License:    GPL
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
* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.17
- Initial RPM

