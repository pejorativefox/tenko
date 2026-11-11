Name:       gcr
Version:    3.41.2
Release:    1
Summary:    GNOME crypto services library and object framework
License:    LGPL-2.1
URL:        https://gitlab.gnome.org/GNOME/gcr
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
GCR is a library for displaying certificates and crypto UI, and accessing
key stores.  It also provides the viewer for crypto files on the GNOME
desktop.

%prep
%setup -q
sed -i 's:"/desktop:"/org:' schema/*.xml

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -D gtk_doc=false    \
      -D ssh_agent=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/gcr.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.41.2-1
- New package, required by libnma
