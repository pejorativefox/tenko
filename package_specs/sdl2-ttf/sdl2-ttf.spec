Name:       sdl2-ttf
Version:    2.24.0
Release:    1
Summary:    SDL2 True type font library
License:    zlib
Source0:    SDL2_ttf-%{version}.tar.gz
Prefix:     /usr

BuildRequires: sdl2
BuildRequires: freetype
BuildRequires: harfbuzz

%description
This is a sample library which allows you to use TrueType fonts in
your SDL applications.

%prep
%setup -q -n SDL2_ttf-%{version}

%build
%configure \
    --disable-static \
    --disable-freetype-builtin \
    --disable-harfbuzz-builtin \
    --enable-harfbuzz
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/sdl2-ttf.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.24.0-1
- Not in the base set; latest SDL2-series upstream release
  (2026-11-05).
- Build shared only against the published SDL2 2.32.74, freetype
  2.15.0 and harfbuzz 15.0.0.
- Refresh %files from the build (no -devel split).
