Name:       python3-pycairo
Version:    1.29.2
Release:    1
Summary:    Python 3 bindings for the cairo graphics library
License:    LGPL-2.1-only OR MPL-1.1
URL:        https://pycairo.readthedocs.io/
Source0:    pycairo-%{version}.tar.gz
Prefix:     /usr

BuildRequires: cairo
BuildRequires: python

%description
pycairo provides Python 3 bindings for most of cairo's drawing API,
including the GTK-integration surfaces.  GIMP 3's Python plug-ins use
it together with PyGObject.

%prep
%setup -q -n pycairo-%{version}

%build
rm -rf build
meson setup build --prefix=/usr --buildtype=release \
      -D tests=false
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-pycairo.filelist

%changelog
* Wed Nov 25 2026 tenko <build@tenko.invalid> 1.29.2-1
- New package, not in the base set: latest upstream stable release
  (1.29.2, checked 2026-11-25); GIMP 3's Python plug-ins use it with
  PyGObject.
- The test suite is not built (-Dtests=false).
