Name:       stunnel 
Version:    5.82
Release:    2
Summary:    TLS proxy daemon.
License:    GPL-2.0-or-later WITH stunnel-exception
Source0:    %{name}-%{version}.tar.gz
Source1:    stunnel-service.conf
Source2:    stunnel.service
Prefix:     /usr

%description
Stunnel is a proxy designed to add TLS encryption functionality to existing clients and servers without any changes in the programs' code. 

%prep
%setup -n stunnel-%{version}

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

mkdir -pv %{buildroot}/etc/finit.d/available
mkdir -pv %{buildroot}/etc/service.d

cp %{SOURCE1} %{buildroot}/etc/finit.d/available/stunnel.conf
cp %{SOURCE2} %{buildroot}/etc/service.d/


%files
/etc/finit.d/available/stunnel.conf
/etc/service.d/stunnel.service
/etc/stunnel/stunnel.conf-sample
/usr/bin/stunnel
/usr/bin/stunnel3
/usr/lib64/stunnel/libstunnel.so
/usr/share/doc/stunnel/AUTHORS.md
/usr/share/doc/stunnel/BUGS.md
/usr/share/doc/stunnel/COPYING.md
/usr/share/doc/stunnel/COPYRIGHT.md
/usr/share/doc/stunnel/CREDITS.md
/usr/share/doc/stunnel/INSTALL.FIPS.md
/usr/share/doc/stunnel/INSTALL.W32.md
/usr/share/doc/stunnel/INSTALL.WCE.md
/usr/share/doc/stunnel/NEWS.md
/usr/share/doc/stunnel/PORTS.md
/usr/share/doc/stunnel/README.md
/usr/share/doc/stunnel/TODO.md
/usr/share/doc/stunnel/examples/ca.html
/usr/share/doc/stunnel/examples/ca.pl
/usr/share/doc/stunnel/examples/importCA.html
/usr/share/doc/stunnel/examples/importCA.sh
/usr/share/doc/stunnel/examples/script.sh
/usr/share/doc/stunnel/examples/stunnel.init
/usr/share/doc/stunnel/examples/stunnel.logrotate
/usr/share/doc/stunnel/examples/stunnel.rh.init
/usr/share/doc/stunnel/examples/stunnel.service
/usr/share/doc/stunnel/examples/stunnel.spec
/usr/share/doc/stunnel/stunnel.html
/usr/share/doc/stunnel/stunnel.pl.html
/usr/share/man/man8/stunnel.8.gz
/usr/share/man/man8/stunnel.pl.8.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.82-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later WITH stunnel-exception): COPYING.md (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 5.82-1
- Sync with the base set

* Mon Jun 12 2023 Chris Statzer <chris.statzer@gmail.com> 5.69
- Version bump

* Thu May 14 2020 Chris Statzer <chris.statzer@qq.com> 5.56-2
- Added finit control script

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 5.56
- Initial package.
