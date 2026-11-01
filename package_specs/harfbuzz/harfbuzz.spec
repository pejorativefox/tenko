Name:       harfbuzz
Version:    14.5.0
Release:    2
Summary:    Text shaping engine
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
The HarfBuzz package contains an OpenType text shaping engine.

%package devel
Summary:    harfbuzz development files
Requires:   harfbuzz = %{version}-%{release}
Provides: pkgconfig(harfbuzz)

%description devel
Development files for harfbuzz.

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
%files devel -f %{_sourcedir}/harfbuzz-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 14.5.0-2
- Split devel payload into harfbuzz-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 14.3.1
- Sync with BLFS r13.1 (8.1.1)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 8.1.1-1
- Version bump
