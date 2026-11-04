Name:       cargo-c
Version:    0.10.26
Release:    1
Summary:    C-ABI compatible library builder for cargo
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
Source1:    Cargo.lock
Source2:    %{name}-%{version}-vendor.tar.xz
BuildRequires: rust

%description
cargo-c provides a cargo subcommand to build and install C-ABI compatible
dynamic and static libraries.  It is required by packages such as librsvg
that expose a Rust implementation through a C API.

%prep
%setup -q
cp %{SOURCE1} Cargo.lock
tar -xf %{SOURCE2}
mkdir -p .cargo
cat > .cargo/config.toml <<'EOF'
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

%build
export PATH=/opt/rust/bin:$PATH
export CARGO_HOME="$PWD/cargo-home"
export CARGO_NET_OFFLINE=true
mkdir -p "$CARGO_HOME"
cargo build --release -j4

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_bindir}
install -m755 target/release/cargo-capi    %{buildroot}%{_bindir}/
install -m755 target/release/cargo-cbuild  %{buildroot}%{_bindir}/
install -m755 target/release/cargo-cinstall %{buildroot}%{_bindir}/
install -m755 target/release/cargo-ctest   %{buildroot}%{_bindir}/

%files
%{_bindir}/cargo-capi
%{_bindir}/cargo-cbuild
%{_bindir}/cargo-cinstall
%{_bindir}/cargo-ctest

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.10.26-1
- Update to 0.10.26 (current BLFS r13.1 trunk).  Vendor tarball regenerated
  from the release Cargo.lock for offline builds; note the book still lists
  the 0.10.25 lock md5, but the actual v0.10.26 release lock is different.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.10.25-1
- New package: cargo-c 0.10.25 (BLFS r13.1), required build tool for librsvg.
  Built with vendored crates for offline builds.
