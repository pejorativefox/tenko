Name:       openvpn
Version:    2.7.8
Release:    1
Summary:    Open source VPN client
License:    GPL-2.0-only WITH OpenSSL-exception
URL:        https://openvpn.net/community/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: openssl
BuildRequires: linux-pam
BuildRequires: libcap-ng

%description
Open source VPN client
OpenVPN is a full-featured SSL VPN which implements OSI layer 2 or 3
secure network extension using the industry standard SSL/TLS protocol.

%prep
%setup -q

%build
%configure \
    --disable-lzo \
    --disable-lz4 \
    --disable-dco
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/openvpn.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.7.8-1
- Not in the base set: bump to the latest upstream
  stable release (2.7.8, checked 2026-11-05). Build with LZO, LZ4
  and DCO disabled because those libraries are not in the repo.
- Requires libcap-ng, added as a new package because 2.7.8 hard-requires
  it on Linux; the PAM and down-root plugins build and are packaged.

* Wed Aug 19 2020 Chris Statzer <chris.statzer@qq.com> 2.4.9
- Initial RPM
