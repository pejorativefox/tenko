Name:       nftables
Version:    1.1.7
Release:    1
Summary:    Netfilter packet filtering framework (the nft command)
License:    GPL-2.0-only AND GPL-2.0-or-later
URL:        https://www.netfilter.org/projects/nftables/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: libmnl
BuildRequires: libnftnl
BuildRequires: gmp
BuildRequires: readline
BuildRequires: jansson

%description
nftables replaces the iptables, ip6tables, arptables and ebtables
frameworks with a single tool, nft, and the libnftables library.

netavark, podman's network stack, uses nft (through its JSON interface,
nft -j) to set up NAT, port forwarding and isolation rules for container
bridge networks.

nftables.service loads /etc/nftables/rules/main.nft at boot.  It is not
enabled, and does nothing until that file exists; the example rule sets
are in /usr/share/nftables.

%prep
%setup -q

%build
# The parser, scanner and man pages are pre-generated in the release
# tarball, so neither bison/flex nor asciidoc is needed.  The interactive
# CLI uses readline (editline is not packaged).  xtables support only
# matters for rules written by iptables-nft, which Tenko does not ship.
%configure \
    --disable-static \
    --with-cli=readline \
    --with-json \
    --without-xtables \
    --with-unitdir=/usr/lib/systemd/system
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/nftables.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 1.1.7-1
- New package, not in the base set: latest upstream stable release
  (1.1.7, checked 2026-11-15).  Firewall backend for netavark's default
  nftables driver (issue #68).
- Built with JSON support (jansson) for nft -j, which netavark uses, and
  the readline CLI; without xtables.
- nftables.service is shipped but not enabled.
