Name:       nss
Version:    3.132
Release:    2
Summary:    Network Security Services libraries
License:    MPL-2.0
URL:        https://firefox-source-docs.mozilla.org/security/nss/index.html
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: nspr
Source1:    nss-standalone-1.patch
Patch0:     nss-standalone-1.patch

%description
Network Security Services (NSS) is a set of libraries designed to support
cross-platform development of security-enabled client and server
applications. NSS supports TLS 1.2, TLS 1.3, PKCS #5, PKCS #7, PKCS #11,
PKCS #12, S/MIME and X.509 v3 certificates.

%prep
%setup -q
%patch -P 0 -p1 -F2

%build
pushd nss
%make_build BUILD_OPT=1                  \
  NSPR_INCLUDE_DIR=/usr/include/nspr  \
  USE_SYSTEM_ZLIB=1                   \
  ZLIB_LIBS=-lz                       \
  NSS_ENABLE_WERROR=0                 \
  $([ $(uname -m) = x86_64 ] && echo USE_64=1) \
  $([ -f /usr/include/sqlite3.h ] && echo NSS_USE_SYSTEM_SQLITE=1)
popd

%install    
rm -rf %{buildroot}

pushd dist
mkdir -pv %{buildroot}/usr/lib64
mkdir -pv %{buildroot}/usr/include/nss
mkdir -pv %{buildroot}/usr/bin
mkdir -pv %{buildroot}/usr/lib64/pkgconfig

install -v -m755 Linux*/lib/*.so              %{buildroot}/usr/lib64
install -v -m644 Linux*/lib/*.chk %{buildroot}/usr/lib64

install -v -m755 -d                           %{buildroot}/usr/include/nss
cp -v -RL {public,private}/nss/*              %{buildroot}/usr/include/nss
chmod -v 644                                  %{buildroot}/usr/include/nss/*

install -v -m755 Linux*/bin/{certutil,nss-config,pk12util} %{buildroot}/usr/bin

install -v -m644 Linux*/lib/pkgconfig/nss.pc  %{buildroot}/usr/lib64/pkgconfig

rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/nss.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.132-2
- Replace the TODO summary/description and record the verified license
  (MPL-2.0): nss/COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.132-1
- Sync with the standalone patch, now unversioned

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 3.92-1
- Version bump
