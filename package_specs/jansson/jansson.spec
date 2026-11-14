Name:       jansson
Version:    2.15.1
Release:    1
Summary:    C library for encoding, decoding and manipulating JSON data
License:    MIT
URL:        https://github.com/akheron/jansson
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

# BuildRequires: none (toolchain only)

%description
Jansson is a C library for encoding, decoding and manipulating JSON data.

nftables uses it for its JSON interface (nft -j), which netavark uses to
program container firewall rules.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/jansson.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 2.15.1-1
- New package, not in the base set: latest upstream stable release
  (2.15.1, checked 2026-11-15).  nftables needs it for nft -j, the JSON
  interface netavark uses (issue #68).
