Name:       tokei
Version:    15.0.0
Release:    3
Summary:    Count your code, quickly
License:    MIT OR Apache-2.0
URL:        https://github.com/XAMPPRocky/tokei
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
ExclusiveArch: x86_64

# Upstream publishes no prebuilt binaries for v15.0.0, so the package is
# built from source with the distro rust toolchain.
BuildRequires: rust
BuildRequires: make-ca

%description
tokei counts lines of code, comments and blanks, broken down per language,
file and directory.  It recognises over 200 languages, ignores files
according to .gitignore/.ignore, and can print JSON, YAML or CBOR output
for tooling.

%prep
%setup -q

%build
export CARGO_HOME="$PWD/cargo-home"
export RUSTFLAGS="-C strip=symbols"
mkdir -p "$CARGO_HOME"
cargo build --locked --release -j4

%install
rm -rf %{buildroot}
install -Dm755 target/release/tokei %{buildroot}%{_bindir}/tokei
install -Dm644 LICENCE-APACHE %{buildroot}%{_licensedir}/tokei/LICENCE-APACHE
install -Dm644 LICENCE-MIT %{buildroot}%{_licensedir}/tokei/LICENCE-MIT

%files -f %{_sourcedir}/tokei.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 15.0.0-3
- Build with the source-built distro rust as an ordinary glibc binary.
  The static musl build relied on upstream's prebuilt musl standard
  library, which only matches upstream's own compiler binaries.

* Fri Nov 13 2026 tenko <build@tenko.invalid> 15.0.0-2
- Download the crates at build time (pinned by Cargo.lock, --locked)
  instead of from a separately hosted vendor bundle.  Same version.

* Tue Nov 10 2026 browneye <build@browneye.invalid> 15.0.0-1
- Initial package.  Tokei is not in the base set.
- Version 15.0.0 is the latest stable upstream release (2026-09-06).
- Upstream publishes no binary assets for v15.0.0, so the package is
  built from source with the shipped rust 1.99.0 toolchain, statically
  linked against musl (Source2) as a single self-contained binary.
- Crates are vendored (Source1) because rpmbuild runs with --network=none.
