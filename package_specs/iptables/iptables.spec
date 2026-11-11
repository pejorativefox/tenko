Name:       iptables
Version:    1.8.13
Release:    2
Summary:    Firewall tool
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Firewall tool

%prep
%setup

%build
sed -i -e '/libebt_/s/^/#/' \
       -e '/libarpt_/s/^/#/' extensions/GNUmakefile.in

%configure  --prefix=/usr      \
            --sbindir=/sbin    \
            --disable-nftables \
            --enable-libipq    \
            --with-xtlibdir=/lib/xtables
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/iptables.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.8.13-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING, plus iptables/iptables.c "either version 2 ... or any later version" (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.8.13-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.8.0
- Initial RPM

