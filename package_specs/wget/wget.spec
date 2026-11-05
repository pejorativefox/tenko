Name:       wget
Version:    1.25.0
Release:    2
Summary:    Non-interactive network downloader
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
GNU Wget is a free utility for non-interactive download of files from the
Web. It supports HTTP, HTTPS and FTP protocols, as well as retrieval through
HTTP proxies.

%prep
%setup -q -a0

%build
NEW_LINE='#if !defined OPENSSL_NO_SSL3_METHOD '
NEW_LINE+='&& OPENSSL_VERSION_NUMBER < 0x40000000L'
sed -i "/SSL3/c $NEW_LINE" src/openssl.c
unset NEW_LINE

%configure --sysconfdir=/etc  \
           --with-ssl=openssl
%make_build 

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/etc/wgetrc
/usr/bin/wget
/usr/share/info/wget.info.gz
/usr/share/locale/af/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/be/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/be/LC_MESSAGES/wget.mo
/usr/share/locale/bg/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/bg/LC_MESSAGES/wget.mo
/usr/share/locale/ca/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/ca/LC_MESSAGES/wget.mo
/usr/share/locale/cs/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/cs/LC_MESSAGES/wget.mo
/usr/share/locale/da/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/da/LC_MESSAGES/wget.mo
/usr/share/locale/de/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/de/LC_MESSAGES/wget.mo
/usr/share/locale/el/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/el/LC_MESSAGES/wget.mo
/usr/share/locale/en_GB/LC_MESSAGES/wget.mo
/usr/share/locale/eo/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/eo/LC_MESSAGES/wget.mo
/usr/share/locale/es/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/es/LC_MESSAGES/wget.mo
/usr/share/locale/et/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/et/LC_MESSAGES/wget.mo
/usr/share/locale/eu/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/eu/LC_MESSAGES/wget.mo
/usr/share/locale/fi/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/fi/LC_MESSAGES/wget.mo
/usr/share/locale/fr/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/fr/LC_MESSAGES/wget.mo
/usr/share/locale/ga/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/ga/LC_MESSAGES/wget.mo
/usr/share/locale/gl/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/gl/LC_MESSAGES/wget.mo
/usr/share/locale/he/LC_MESSAGES/wget.mo
/usr/share/locale/hr/LC_MESSAGES/wget.mo
/usr/share/locale/hu/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/hu/LC_MESSAGES/wget.mo
/usr/share/locale/id/LC_MESSAGES/wget.mo
/usr/share/locale/it/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/it/LC_MESSAGES/wget.mo
/usr/share/locale/ja/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/ja/LC_MESSAGES/wget.mo
/usr/share/locale/ka/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/ka/LC_MESSAGES/wget.mo
/usr/share/locale/ko/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/ko/LC_MESSAGES/wget.mo
/usr/share/locale/lt/LC_MESSAGES/wget.mo
/usr/share/locale/ms/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/nb/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/nb/LC_MESSAGES/wget.mo
/usr/share/locale/nl/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/nl/LC_MESSAGES/wget.mo
/usr/share/locale/pl/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/pl/LC_MESSAGES/wget.mo
/usr/share/locale/pt/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/pt/LC_MESSAGES/wget.mo
/usr/share/locale/pt_BR/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/pt_BR/LC_MESSAGES/wget.mo
/usr/share/locale/ro/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/ro/LC_MESSAGES/wget.mo
/usr/share/locale/ru/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/ru/LC_MESSAGES/wget.mo
/usr/share/locale/rw/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/sk/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/sk/LC_MESSAGES/wget.mo
/usr/share/locale/sl/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/sl/LC_MESSAGES/wget.mo
/usr/share/locale/sr/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/sr/LC_MESSAGES/wget.mo
/usr/share/locale/sv/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/sv/LC_MESSAGES/wget.mo
/usr/share/locale/tr/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/tr/LC_MESSAGES/wget.mo
/usr/share/locale/uk/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/uk/LC_MESSAGES/wget.mo
/usr/share/locale/vi/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/vi/LC_MESSAGES/wget.mo
/usr/share/locale/zh_CN/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/zh_CN/LC_MESSAGES/wget.mo
/usr/share/locale/zh_TW/LC_MESSAGES/wget-gnulib.mo
/usr/share/locale/zh_TW/LC_MESSAGES/wget.mo
/usr/share/man/man1/wget.1.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.25.0-2
- Replace the TODO summary/description and record the verified license
  (GPL-3.0-or-later): src/main.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.25.0-1
- Sync with BLFS r13.1

# let's skip this for now
