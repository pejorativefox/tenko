%global rust_version 1.99.0
%global musl_target  x86_64-unknown-linux-musl

Name:       tokei
Version:    15.0.0
Release:    1
Summary:    Count your code, quickly
License:    MIT OR Apache-2.0
URL:        https://github.com/XAMPPRocky/tokei
Source0:    %{name}-%{version}.tar.gz
Source1:    %{name}-%{version}-vendor.tar.xz
Source2:    rust-std-%{rust_version}-%{musl_target}.tar.gz
Prefix:     /usr
ExclusiveArch: x86_64

# Upstream publishes no prebuilt binaries for v15.0.0, so the package is
# built from source against the shipped rust toolchain.  The musl standard
# library (Source2) is not part of the rust package; it is unpacked into a
# private sysroot in %prep so the result is a single static-pie binary with
# no runtime dependencies.
BuildRequires: rust = %{rust_version}

%description
tokei counts lines of code, comments and blanks, broken down per language,
file and directory.  It recognises over 200 languages, ignores files
according to .gitignore/.ignore, and can print JSON, YAML or CBOR output
for tooling.

%prep
%setup -q
tar -xf %{SOURCE1}

# Build a private sysroot: the host toolchain from /opt/rust plus the musl
# standard library, which the rust package does not ship.
mkdir -p sysroot/lib/rustlib
ln -s /opt/rust/bin sysroot/bin
ln -s /opt/rust/share sysroot/share
for f in /opt/rust/lib/*; do
    case "$f" in
        */rustlib) continue ;;
    esac
    ln -s "$f" sysroot/lib/
done
for f in /opt/rust/lib/rustlib/*; do
    case "$f" in
        */%{musl_target}) continue ;;
    esac
    ln -s "$f" sysroot/lib/rustlib/
done
tar -xzf %{SOURCE2}
cp -a rust-std-%{rust_version}-%{musl_target}/rust-std-%{musl_target}/lib/rustlib/%{musl_target} \
      sysroot/lib/rustlib/

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
export RUSTFLAGS="--sysroot=$PWD/sysroot -C linker=/opt/rust/lib/rustlib/x86_64-unknown-linux-gnu/bin/rust-lld -C strip=symbols"
mkdir -p "$CARGO_HOME"
cargo build --release --target %{musl_target} -j4

%install
rm -rf %{buildroot}
install -Dm755 target/%{musl_target}/release/tokei %{buildroot}%{_bindir}/tokei
install -Dm644 LICENCE-APACHE %{buildroot}%{_licensedir}/tokei/LICENCE-APACHE
install -Dm644 LICENCE-MIT %{buildroot}%{_licensedir}/tokei/LICENCE-MIT

%files -f %{_sourcedir}/tokei.filelist

%changelog
* Tue Nov 10 2026 browneye <build@browneye.invalid> 15.0.0-1
- Initial package.  Tokei is not in the base set.
- Version 15.0.0 is the latest stable upstream release (2026-09-06).
- Upstream publishes no binary assets for v15.0.0, so the package is
  built from source with the shipped rust 1.99.0 toolchain, statically
  linked against musl (Source2) as a single self-contained binary.
- Crates are vendored (Source1) because rpmbuild runs with --network=none.
