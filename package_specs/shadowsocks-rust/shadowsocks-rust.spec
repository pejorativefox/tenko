Name:       shadowsocks-rust
Version:    1.25.0
Release:    1
Summary:    Rust port of shadowsocks, a secure SOCKS5 tunnel proxy
License:    MIT
URL:        https://github.com/shadowsocks/shadowsocks-rust
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
ExclusiveArch: x86_64

BuildRequires: rust
BuildRequires: make-ca
# aws-lc-sys (TLS for DNS-over-TLS/HTTPS and HTTP local mode) builds its C
# sources with CMake.
BuildRequires: cmake

%description
shadowsocks-rust is a Rust implementation of the shadowsocks tunnel proxy.
It provides the client (sslocal), server (ssserver), manager (ssmanager),
URL/QR utility (ssurl) and multi-instance service wrapper (ssservice)
commands, with AEAD and AEAD-2022 ciphers, SOCKS5, HTTP, tunnel and
transparent-redirect client modes, and DNS-over-TLS/HTTPS resolution.

Two systemd template units run one instance per configuration file:
`systemctl enable --now shadowsocks-rust-local@<name>` reads
/etc/shadowsocks-rust/<name>.json, and
`shadowsocks-rust-server@<name>` does the same for a server instance.  An
example configuration is installed as
/usr/share/shadowsocks-rust/config.json.example.

%prep
%setup -q

%build
export CARGO_HOME="$PWD/cargo-home"
export RUSTFLAGS="-C strip=symbols"
mkdir -p "$CARGO_HOME"
cargo build --locked --release %{?_smp_mflags}

%install
rm -rf %{buildroot}
for cmd in sslocal ssserver ssmanager ssurl ssservice; do
    install -Dm755 target/release/$cmd %{buildroot}%{_bindir}/$cmd
done
install -Dm644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE

install -Dm644 %{_sourcedir}/shadowsocks-rust-local@.service \
    %{buildroot}%{_unitdir}/shadowsocks-rust-local@.service
install -Dm644 %{_sourcedir}/shadowsocks-rust-server@.service \
    %{buildroot}%{_unitdir}/shadowsocks-rust-server@.service
install -Dm644 debian/config.json \
    %{buildroot}%{_datadir}/shadowsocks-rust/config.json.example

%files -f %{_sourcedir}/shadowsocks-rust.filelist

%changelog
* Tue Nov 17 2026 tenko <build@tenko.invalid> 1.25.0-1
- New package, not in the base set: latest upstream stable release
  (1.25.0, checked 2026-11-17).  Built from source with the distro rust
  toolchain; crates are downloaded at build time and pinned by Cargo.lock
  (--locked).  Installs the five upstream commands, the upstream systemd
  template units (one instance per /etc/shadowsocks-rust/<name>.json) and
  the upstream example configuration.
