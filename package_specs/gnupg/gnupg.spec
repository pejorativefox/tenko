Name:       gnupg
Version:    2.5.24
Release:    1
Summary:    GNU's tool for secure communication and data storage.
License:    GPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
GNU's tool for secure communication and data storage.

%prep
%setup

%build
%configure --enable-symcryptrun     \
           --docdir=/usr/share/doc/gnupg-2.2.9
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -rf %{buildroot}/usr/share/info/dir

%files
/usr/bin/addgnupghome
/usr/bin/applygnupgdefaults
/usr/bin/dirmngr
/usr/bin/dirmngr-client
/usr/bin/gpg
/usr/bin/gpg-agent
/usr/bin/gpg-authcode-sign.sh
/usr/bin/gpg-card
/usr/bin/gpg-connect-agent
/usr/bin/gpg-mail-tube
/usr/bin/gpg-wks-client
/usr/bin/gpg-wks-server
/usr/bin/gpgconf
/usr/bin/gpgparsemail
/usr/bin/gpgscm
/usr/bin/gpgsm
/usr/bin/gpgsplit
/usr/bin/gpgtar
/usr/bin/gpgv
/usr/bin/kbxutil
/usr/bin/watchgnupg
/usr/libexec/gpg-auth
/usr/libexec/gpg-check-pattern
/usr/libexec/gpg-pair-tool
/usr/libexec/gpg-preset-passphrase
/usr/libexec/gpg-protect-tool
/usr/libexec/gpg-wks-client
/usr/libexec/keyboxd
/usr/libexec/scdaemon
/usr/share/doc/gnupg-2.2.9/DCO
/usr/share/doc/gnupg-2.2.9/DETAILS
/usr/share/doc/gnupg-2.2.9/FAQ
/usr/share/doc/gnupg-2.2.9/HACKING
/usr/share/doc/gnupg-2.2.9/KEYSERVER
/usr/share/doc/gnupg-2.2.9/OpenPGP
/usr/share/doc/gnupg-2.2.9/README
/usr/share/doc/gnupg-2.2.9/TRANSLATE
/usr/share/doc/gnupg-2.2.9/examples/README
/usr/share/doc/gnupg-2.2.9/examples/common.conf
/usr/share/doc/gnupg-2.2.9/examples/gpgconf.conf
/usr/share/doc/gnupg-2.2.9/examples/gpgconf.rnames
/usr/share/doc/gnupg-2.2.9/examples/pwpattern.list
/usr/share/doc/gnupg-2.2.9/examples/qualified.txt
/usr/share/doc/gnupg-2.2.9/examples/scd-event
/usr/share/doc/gnupg-2.2.9/examples/trustlist.txt
/usr/share/gnupg/distsigkey.gpg
/usr/share/gnupg/help.be.txt
/usr/share/gnupg/help.ca.txt
/usr/share/gnupg/help.cs.txt
/usr/share/gnupg/help.da.txt
/usr/share/gnupg/help.de.txt
/usr/share/gnupg/help.el.txt
/usr/share/gnupg/help.eo.txt
/usr/share/gnupg/help.es.txt
/usr/share/gnupg/help.et.txt
/usr/share/gnupg/help.fi.txt
/usr/share/gnupg/help.fr.txt
/usr/share/gnupg/help.gl.txt
/usr/share/gnupg/help.hu.txt
/usr/share/gnupg/help.id.txt
/usr/share/gnupg/help.it.txt
/usr/share/gnupg/help.ja.txt
/usr/share/gnupg/help.nb.txt
/usr/share/gnupg/help.pl.txt
/usr/share/gnupg/help.pt.txt
/usr/share/gnupg/help.pt_BR.txt
/usr/share/gnupg/help.ro.txt
/usr/share/gnupg/help.ru.txt
/usr/share/gnupg/help.sk.txt
/usr/share/gnupg/help.sv.txt
/usr/share/gnupg/help.tr.txt
/usr/share/gnupg/help.txt
/usr/share/gnupg/help.zh_CN.txt
/usr/share/gnupg/help.zh_TW.txt
/usr/share/gnupg/mail-tube.de.txt
/usr/share/gnupg/mail-tube.txt
/usr/share/gnupg/wks-utils.de.txt
/usr/share/gnupg/wks-utils.txt
/usr/share/info/gnupg.info-1.gz
/usr/share/info/gnupg.info-2.gz
/usr/share/info/gnupg.info-3.gz
/usr/share/info/gnupg.info.gz
/usr/share/locale/ca/LC_MESSAGES/gnupg2.mo
/usr/share/locale/cs/LC_MESSAGES/gnupg2.mo
/usr/share/locale/da/LC_MESSAGES/gnupg2.mo
/usr/share/locale/de/LC_MESSAGES/gnupg2.mo
/usr/share/locale/el/LC_MESSAGES/gnupg2.mo
/usr/share/locale/en@boldquot/LC_MESSAGES/gnupg2.mo
/usr/share/locale/en@quot/LC_MESSAGES/gnupg2.mo
/usr/share/locale/eo/LC_MESSAGES/gnupg2.mo
/usr/share/locale/es/LC_MESSAGES/gnupg2.mo
/usr/share/locale/et/LC_MESSAGES/gnupg2.mo
/usr/share/locale/fi/LC_MESSAGES/gnupg2.mo
/usr/share/locale/fr/LC_MESSAGES/gnupg2.mo
/usr/share/locale/gl/LC_MESSAGES/gnupg2.mo
/usr/share/locale/hu/LC_MESSAGES/gnupg2.mo
/usr/share/locale/id/LC_MESSAGES/gnupg2.mo
/usr/share/locale/it/LC_MESSAGES/gnupg2.mo
/usr/share/locale/ja/LC_MESSAGES/gnupg2.mo
/usr/share/locale/ka/LC_MESSAGES/gnupg2.mo
/usr/share/locale/nb/LC_MESSAGES/gnupg2.mo
/usr/share/locale/nl/LC_MESSAGES/gnupg2.mo
/usr/share/locale/pl/LC_MESSAGES/gnupg2.mo
/usr/share/locale/pt/LC_MESSAGES/gnupg2.mo
/usr/share/locale/ro/LC_MESSAGES/gnupg2.mo
/usr/share/locale/ru/LC_MESSAGES/gnupg2.mo
/usr/share/locale/sk/LC_MESSAGES/gnupg2.mo
/usr/share/locale/sv/LC_MESSAGES/gnupg2.mo
/usr/share/locale/tr/LC_MESSAGES/gnupg2.mo
/usr/share/locale/uk/LC_MESSAGES/gnupg2.mo
/usr/share/locale/zh_CN/LC_MESSAGES/gnupg2.mo
/usr/share/locale/zh_TW/LC_MESSAGES/gnupg2.mo
/usr/share/man/man1/dirmngr-client.1.gz
/usr/share/man/man1/gpg-agent.1.gz
/usr/share/man/man1/gpg-card.1.gz
/usr/share/man/man1/gpg-check-pattern.1.gz
/usr/share/man/man1/gpg-connect-agent.1.gz
/usr/share/man/man1/gpg-mail-tube.1.gz
/usr/share/man/man1/gpg-preset-passphrase.1.gz
/usr/share/man/man1/gpg-wks-client.1.gz
/usr/share/man/man1/gpg-wks-server.1.gz
/usr/share/man/man1/gpg.1.gz
/usr/share/man/man1/gpgconf.1.gz
/usr/share/man/man1/gpgparsemail.1.gz
/usr/share/man/man1/gpgsm.1.gz
/usr/share/man/man1/gpgtar.1.gz
/usr/share/man/man1/gpgv.1.gz
/usr/share/man/man1/scdaemon.1.gz
/usr/share/man/man1/watchgnupg.1.gz
/usr/share/man/man7/gnupg.7.gz
/usr/share/man/man8/addgnupghome.8.gz
/usr/share/man/man8/applygnupgdefaults.8.gz
/usr/share/man/man8/dirmngr.8.gz

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.5.24-1
- Sync with BLFS r13.1

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 2.2.9
- Initial RPM

