Name:       harfbuzz
Version:    14.5.0
Release:    1
Summary:    Text shaping engine
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
Provides: pkgconfig(harfbuzz)

%description
The HarfBuzz package contains an OpenType text shaping engine.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..              \
      --prefix=/usr         \
      --buildtype=release   \
      -D graphite2=disabled \
      -D introspection=enabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/harfbuzz.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 14.3.1
- Sync with BLFS r13.1 (8.1.1)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 8.1.1-1
- Version bump
