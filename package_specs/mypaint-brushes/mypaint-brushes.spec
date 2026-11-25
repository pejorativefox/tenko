Name:       mypaint-brushes
Version:    2.0.2
Release:    1
Summary:    Default brush set for the MyPaint brush engine
License:    CC0-1.0
URL:        https://github.com/mypaint/mypaint-brushes
Source0:    mypaint-brushes-%{version}.tar.xz
Prefix:     /usr

# BuildRequires: none (toolchain only)

%description
The default MyPaint brush collection, installed as data under
/usr/share/mypaint-brushes together with the mypaint-brushes-2.0
pkg-config entry that GIMP 3 and libmypaint consumers look up.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/mypaint-brushes.filelist

%changelog
* Wed Nov 25 2026 tenko <build@tenko.invalid> 2.0.2-1
- New package, not in the base set: latest upstream stable release
  (2.0.2, checked 2026-11-25); GIMP 3 uses the brushes through
  libmypaint.
- Data-only package: no code is compiled, and the brushes are
  dedicated to the public domain (CC0-1.0 per COPYING).
