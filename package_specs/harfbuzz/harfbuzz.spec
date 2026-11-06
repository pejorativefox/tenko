Name:       harfbuzz
Version:    15.0.0
Release:    3
Summary:    Text shaping engine
License:    MIT
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
      -D cairo=disabled     \
      -D icu=disabled       \
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

%package gir
Summary:    GObject Introspection data for harfbuzz
License:    MIT
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for harfbuzz, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/harfbuzz.filelist
%files gir -f %{_sourcedir}/harfbuzz-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 15.0.0-3
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 15.0.0-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).
- Disable the Cairo and ICU sub-libraries explicitly.  The build image
  ships their headers, while the image the published package was built
  in did not, so autodetection would add harfbuzz-cairo/harfbuzz-icu.

* Mon Nov  2 2026 browneye <build@browneye.invalid> 15.0.0-1
- Update to 15.0.0 (current upstream version).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 14.5.0-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 14.5.0-2
- Split devel payload into harfbuzz-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 14.3.1
- Sync with 8.1.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 8.1.1-1
- Version bump
