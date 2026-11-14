Name:       aardvark-dns
Version:    2.1.0
Release:    1
Summary:    Authoritative DNS server for podman container networks
License:    Apache-2.0
URL:        https://github.com/containers/aardvark-dns
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
ExclusiveArch: x86_64

BuildRequires: rust
BuildRequires: make-ca

%description
aardvark-dns is an authoritative DNS server for A/AAAA container records
on podman networks, forwarding other queries to the host's resolvers.
netavark starts it; the binary is installed as
/usr/libexec/podman/aardvark-dns, where podman and netavark look for it.

%prep
%setup -q

%build
export CARGO_HOME="$PWD/cargo-home"
export RUSTFLAGS="-C strip=symbols"
mkdir -p "$CARGO_HOME"
cargo build --locked --release %{?_smp_mflags}

%install
rm -rf %{buildroot}
install -Dm755 target/release/aardvark-dns \
    %{buildroot}%{_libexecdir}/podman/aardvark-dns
install -Dm644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE

%files -f %{_sourcedir}/aardvark-dns.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 2.1.0-1
- New package, not in the base set: latest upstream stable release
  (2.1.0, checked 2026-11-14).  Source-built podman stack (issue #67).
- Crates downloaded at build time, pinned by Cargo.lock (--locked).
- Man pages are not built: they need go-md2man, which is not packaged yet.
