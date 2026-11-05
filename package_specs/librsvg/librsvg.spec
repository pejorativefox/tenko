Name:       librsvg
Version:    2.63.4
Release:    3
Summary:    SVG rendering library
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
Source1:    %{name}-%{version}-vendor.tar.xz
BuildRequires: cairo
BuildRequires: pango
BuildRequires: gdk-pixbuf
BuildRequires: gobject-introspection
BuildRequires: libxml2
BuildRequires: freetype
BuildRequires: harfbuzz
BuildRequires: rust
BuildRequires: cargo-c

Provides:   pkgconfig(librsvg-2.0)
%description
librsvg is a library and tools used to manipulate, convert and view
Scalable Vector Graphic (SVG) images.

%package gir
Summary:    GObject Introspection data for librsvg
License:    LGPL-2.1-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for librsvg, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%prep
%setup -q
tar -xf %{SOURCE1}
mkdir -p .cargo
cat > .cargo/config.toml <<'EOF'
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF
sed -e "/OUTDIR/s|,| / 'librsvg-%{version}', '--no-namespace-dir',|" \
    -e '/output/s|Rsvg-2.0|librsvg-%{version}|'                            \
    -i doc/meson.build

%build
export PATH=/opt/rust/bin:$PATH
export CARGO_HOME="$PWD/cargo-home"
export CARGO_NET_OFFLINE=true
export CARGO_BUILD_JOBS=4
mkdir -p "$CARGO_HOME"
mkdir build
pushd build
meson setup ..                \
      --prefix=/usr           \
      --buildtype=release     \
      --wrap-mode=nofallback  \
      -D introspection=enabled \
      -D pixbuf-loader=enabled \
      -D vala=disabled        \
      -D docs=disabled        \
      -D tests=false
ninja %{?_smp_mflags}
popd

%install
rm -rf %{buildroot}
export PATH=/opt/rust/bin:$PATH
export CARGO_HOME="$PWD/cargo-home"
export CARGO_NET_OFFLINE=true
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%post
# The pixbuf loader is installed after gdk-pixbuf; regenerate its cache so
# SVG images resolve at runtime.  Image builds with scriptlets disabled must
# run gdk-pixbuf-query-loaders --update-cache (or rebuild gdk-pixbuf).
if [ -x /usr/bin/gdk-pixbuf-query-loaders ]; then
    /usr/bin/gdk-pixbuf-query-loaders --update-cache >/dev/null 2>&1 || :
fi

%postun
if [ -x /usr/bin/gdk-pixbuf-query-loaders ]; then
    /usr/bin/gdk-pixbuf-query-loaders --update-cache >/dev/null 2>&1 || :
fi

%files -f %{_sourcedir}/librsvg.filelist
%files gir -f %{_sourcedir}/librsvg-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.63.4-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.63.4-2
- Split the GObject Introspection typelib into %{name}-gir; the -devel
  package now requires it (last typelib still in a runtime package)

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.63.4-1
- Update to 2.63.4 (current BLFS r13.1 trunk).  Vendor tarball regenerated
  from the shipped Cargo.lock now that the Rust 1.99.0 toolchain and
  cargo-c 0.10.26 are available.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.63.2-2
- Refresh the gdk-pixbuf loader cache in %post/%postun so the SVG loader
  is usable without rebuilding gdk-pixbuf

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.63.2-1
- Sync with BLFS r13.1 (librsvg 2.63.2); port build to Meson + Rust
  with vendored crates; enable the gdk-pixbuf SVG loader.
