Name:       cargo-c
Version:    0.10.26
Release:    2
Summary:    C-ABI compatible library builder for cargo
License:    MIT
URL:        https://github.com/lu-zero/cargo-c
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
Source1:    Cargo.lock
BuildRequires: rust
BuildRequires: make-ca

%description
cargo-c provides a cargo subcommand to build and install C-ABI compatible
dynamic and static libraries.  It is required by packages such as librsvg
that expose a Rust implementation through a C API.

%prep
%setup -q
cp %{SOURCE1} Cargo.lock

%build
export CARGO_HOME="$PWD/cargo-home"
mkdir -p "$CARGO_HOME"
cargo build --locked --release -j4

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_bindir}
install -m755 target/release/cargo-capi    %{buildroot}%{_bindir}/
install -m755 target/release/cargo-cbuild  %{buildroot}%{_bindir}/
install -m755 target/release/cargo-cinstall %{buildroot}%{_bindir}/
install -m755 target/release/cargo-ctest   %{buildroot}%{_bindir}/

%files -f %{_sourcedir}/cargo-c.filelist

%changelog
* Fri Nov 13 2026 tenko <build@tenko.invalid> 0.10.26-2
- Download the crates at build time (pinned by Cargo.lock, --locked)
  instead of from a separately hosted vendor bundle.  Same version.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.10.26-1
- Update to 0.10.26 (current upstream).  Vendor tarball regenerated
  from the release Cargo.lock for offline builds; note tenko.lock still lists
  the 0.10.25 lock md5, but the actual v0.10.26 release lock is different.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.10.25-1
- New package: cargo-c 0.10.25, required build tool for librsvg.
  Built with vendored crates for offline builds.
