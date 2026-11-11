Name:       samba
Version:    4.25.1
Release:    1
Summary:    SMB/CIFS file server and client utilities
License:    GPL-3.0-or-later AND LGPL-3.0-or-later AND BSD-3-Clause
URL:        https://www.samba.org/
Source0:    samba-4.25.1.tar.gz
Source1:    samba.tmpfiles
Source2:    samba.smb.conf
Prefix:     /usr

BuildRequires: gcc
BuildRequires: make
BuildRequires: python
BuildRequires: perl
BuildRequires: flex
BuildRequires: bison
BuildRequires: gnutls
BuildRequires: intltool
BuildRequires: parse-yapp
BuildRequires: dbus-libs
BuildRequires: libbsd
BuildRequires: libtasn1

Requires:   systemd
Requires:   gnutls
Requires:   libarchive
Requires:   python

%description
Samba provides SMB/CIFS file and print services and the client libraries
and utilities used to access SMB shares.  This build supplies
libsmbclient/smbclient for GVFS/Thunar SMB browsing and the standalone
smbd/nmbd file server.

%prep
%setup -q
# Samba 4.25's bundled waf calls the argparse formatter with the Python
# 3.15 "file" argument.  Without this one-line compatibility fix,
# ./configure aborts while printing an error/help message.
sed -i 's/def _get_formatter(self):/def _get_formatter(self, file=None):/' \
    third_party/waf/waflib/Options.py

%build
./configure                                                   \
    --prefix=/usr                                             \
    --libdir=/usr/lib64                                       \
    --sysconfdir=/etc                                         \
    --localstatedir=/var                                      \
    --enable-fhs                                              \
    --without-ad-dc                                           \
    --without-ads                                             \
    --without-ldap                                            \
    --without-json                                            \
    --without-winbind                                         \
    --without-pam                                             \
    --disable-cups                                            \
    --disable-iprint                                          \
    --disable-avahi                                           \
    --disable-glusterfs                                       \
    --disable-cephfs                                          \
    --disable-cephrgw                                         \
    --disable-spotlight                                       \
    --disable-wsp                                             \
    --without-quotas                                          \
    --without-dmapi                                           \
    --without-fam                                             \
    --without-gpgme                                           \
    --disable-python                                          \
    --without-ldb-lmdb                                        \
    --with-systemd                                            \
    --systemd-install-services                                \
    --with-systemddir=/usr/lib/systemd/system                 \
    --with-piddir=/run/samba                                  \
    --with-sockets-dir=/run/samba                             \
    --with-lockdir=/var/lib/samba/lock                        \
    --with-statedir=/var/lib/samba                            \
    --with-cachedir=/var/cache/samba                          \
    --with-logfilebase=/var/log/samba
%make_build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
# The AD DC and winbind daemons are not built with the options above, so
# their units would point at missing executables.
rm -f %{buildroot}%{_unitdir}/samba.service
rm -f %{buildroot}%{_unitdir}/winbind.service
rmdir %{buildroot}/var/lib/samba/bind-dns 2>/dev/null || :
install -Dm644 %{SOURCE1} %{buildroot}/usr/lib/tmpfiles.d/samba.conf
install -Dm644 %{SOURCE2} %{buildroot}/etc/samba/smb.conf

%post
if [ -x /usr/sbin/ldconfig ]; then
    /usr/sbin/ldconfig
fi
if [ -x /usr/bin/systemd-tmpfiles ]; then
    /usr/bin/systemd-tmpfiles --create /usr/lib/tmpfiles.d/samba.conf || :
fi

%postun
if [ -x /usr/sbin/ldconfig ]; then
    /usr/sbin/ldconfig
fi

%files -f %{_sourcedir}/samba.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 4.25.1-1
- New package: Samba 4.25.1 (latest stable upstream), built for the
  Tenko desktop's SMB browsing stack.  Installs libsmbclient, smbclient
  and smbclient.pc for GVFS, plus the standalone smbd/nmbd file server.
- Build without AD DC, ADS, LDAP, JSON, winbind, PAM, CUPS, Avahi,
  GlusterFS, Ceph and the LMDB LDB backend; use the bundled Heimdal.
- Patch the bundled waf for the Python 3.15 argparse formatter signature.
- Ship the SMB/NMB systemd units, a minimal /etc/samba/smb.conf and a
  tmpfiles rule for the runtime/state directories.
