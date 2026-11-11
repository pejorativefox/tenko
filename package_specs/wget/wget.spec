Name:       wget
Version:    1.25.0
Release:    2
Summary:    Non-interactive network downloader
License:    GPL-3.0-or-later
URL:        https://www.gnu.org/software/wget/
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

%files -f %{_sourcedir}/wget.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.25.0-2
- Replace the TODO summary/description and record the verified license
  (GPL-3.0-or-later): src/main.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.25.0-1
- Sync with the base set

# let's skip this for now
