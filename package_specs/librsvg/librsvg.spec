Name:       librsvg
Version:    2.63.2
Release:    1
Summary:    SVG rendering library
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
Source1:    %{name}-%{version}-vendor.tar.xz
BuildRequires: cairo-devel
BuildRequires: pango-devel
BuildRequires: gdk-pixbuf-devel
BuildRequires: gobject-introspection
BuildRequires: libxml2-devel
BuildRequires: freetype-devel
BuildRequires: harfbuzz-devel
BuildRequires: rust
BuildRequires: cargo-c

%description
librsvg is a library and tools used to manipulate, convert and view
Scalable Vector Graphic (SVG) images.

%package devel
Summary:    librsvg development files
Requires:   librsvg = %{version}-%{release}
Provides:   pkgconfig(librsvg-2.0)

%description devel
Development files for librsvg.

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

%files -f %{_sourcedir}/librsvg.filelist
%files devel -f %{_sourcedir}/librsvg-devel.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.63.2-1
- Sync with BLFS r13.1 (librsvg 2.63.2); port build to Meson + Rust
  with vendored crates; enable the gdk-pixbuf SVG loader.
