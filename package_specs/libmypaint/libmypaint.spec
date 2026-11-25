Name:       libmypaint
Version:    1.6.1
Release:    1
Summary:    MyPaint brush engine as a standalone library
License:    ISC
URL:        https://github.com/mypaint/libmypaint
Source0:    libmypaint-%{version}.tar.xz
Prefix:     /usr

BuildRequires: glib
BuildRequires: gobject-introspection

%description
libmypaint is the brush dynamics engine developed for MyPaint,
available as a standalone C library with GObject introspection.
GIMP 3 uses it together with the mypaint-brushes-2.0 data package
to load MyPaint brush presets.

%package lang
Summary:    libmypaint translations
Requires:   libmypaint = %{version}-%{release}

%description lang
Translations for libmypaint.

%prep
%setup -q

%build
%configure --disable-static --enable-introspection
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libmypaint.filelist
%files lang -f %{_sourcedir}/libmypaint-lang.filelist

%changelog
* Wed Nov 25 2026 tenko <build@tenko.invalid> 1.6.1-1
- New package, not in the base set: latest upstream stable release
  (1.6.1, checked 2026-11-25); GIMP 3 loads MyPaint brush dynamics
  through it.
- GObject introspection is enabled; the typelibs stay in the main
  package following the json-glib layout.
