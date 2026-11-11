Name:       gsettings-desktop-schemas
Version:    51.0
Release:    1
Summary:    Shared GSettings schemas for the GNOME desktop
License:    LGPL-2.1
URL:        https://gitlab.gnome.org/GNOME/gsettings-desktop-schemas
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
gsettings-desktop-schemas contains the shared GSettings schemas for the
GNOME desktop, used by glib-networking and other GNOME components.

%prep
%setup -q
sed -i -r 's:"(/system):"/org/gnome\1:g' schemas/*.in

%build
mkdir build
pushd build
meson setup --prefix=/usr --buildtype=release ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/gsettings-desktop-schemas.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 51.0-1
- New package, required by glib-networking 2.90.1
