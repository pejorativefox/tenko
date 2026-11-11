Name:       libnma
Version:    1.10.6
Release:    1
Summary:    NetworkManager GUI library
License:    LGPL-2.1
URL:        https://gitlab.gnome.org/GNOME/libnma
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: NetworkManager
BuildRequires: cairo
BuildRequires: gcr
BuildRequires: gtk+
BuildRequires: iso-codes

%description
libnma provides a shared library used by NetworkManager's GUI clients
(GTK3 widgets for connection editing and secrets).

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                                  \
      --prefix=/usr                             \
      --buildtype=release                       \
      -D gtk_doc=false                          \
      -D libnma_gtk4=false                      \
      -D mobile_broadband_provider_info=false \
      -D introspection=false                    \
      -D vapi=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libnma.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.10.6-1
- New package, required by network-manager-applet
