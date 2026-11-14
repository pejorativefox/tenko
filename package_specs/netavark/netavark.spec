Name:       netavark
Version:    2.1.0
Release:    2
Summary:    Container network stack for podman
License:    Apache-2.0
URL:        https://github.com/containers/netavark
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
ExclusiveArch: x86_64

# build.rs compiles the DHCP proxy's gRPC definitions with
# tonic-prost-build, which runs protoc.
BuildRequires: rust
BuildRequires: make-ca
BuildRequires: protobuf

# The default firewall driver runs nft (through nft -j) for NAT, port
# forwarding and network isolation.
Requires:      nftables

%description
netavark is the network stack podman uses to set up container networking:
bridge, macvlan and ipvlan networks, port forwarding, DHCP (through
netavark-dhcp-proxy) and DNS through aardvark-dns.  The binary is
installed as /usr/libexec/podman/netavark, where podman looks for it.

The default firewall driver is nftables, which runs the nft command for
container NAT, port forwarding and network isolation.  The systemd units
for the DHCP proxy and for reapplying the rules after a firewalld or
nftables reload are shipped but not enabled.

%prep
%setup -q

%build
export CARGO_HOME="$PWD/cargo-home"
export RUSTFLAGS="-C strip=symbols"
export PROTOC=/usr/bin/protoc
mkdir -p "$CARGO_HOME" bin
cargo build --locked --release %{?_smp_mflags} --bin netavark
cp target/release/netavark bin/netavark

%install
rm -rf %{buildroot}
make install.netavark install.systemd DESTDIR=%{buildroot} PREFIX=%{_prefix} \
    SYSTEMDDIR=/usr/lib/systemd/system SELINUXOPT=
install -Dm644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE

%files -f %{_sourcedir}/netavark.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 2.1.0-2
- Require nftables: the default firewall driver runs nft for bridge
  network NAT and port forwarding (issue #68).  Same upstream version.

* Sat Nov 14 2026 tenko <build@tenko.invalid> 2.1.0-1
- New package, not in the base set: latest upstream stable release
  (2.1.0, checked 2026-11-14).  Source-built podman stack (issue #67).
- Crates downloaded at build time, pinned by Cargo.lock (--locked).
- Default firewall driver left at nftables; nftables is not packaged yet,
  so there is no hard requirement on it.
- Man pages are not built: they need go-md2man, which is not packaged yet.
