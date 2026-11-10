Name:       python3-dbus
Version:    1.5.1
Release:    1
Summary:    Python bindings for D-Bus
License:    MIT
URL:        https://gitlab.freedesktop.org/dbus/dbus-python
Source0:    dbus-python-%{version}.tar.gz
Prefix:     /usr
BuildRequires: dbus-daemon
BuildRequires: glib
BuildRequires: meson
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: python
Requires:   dbus-libs
Requires:   python3-gobject

%description
dbus-python provides the dbus Python package: low-level D-Bus bindings,
the dbus.service and dbus.proxies helper classes, and the GLib main-loop
integration used by TuneD's D-Bus service.

%prep
%setup -q -n dbus_python-%{version}

%build
rm -rf build
meson setup build --prefix=/usr --buildtype=release -Dtests=disabled
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-dbus.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 1.5.1-1
- New package: dbus-python 1.5.1 (latest stable upstream).  Not in the base
  set; TuneD's D-Bus service and tuned-adm client require it.
