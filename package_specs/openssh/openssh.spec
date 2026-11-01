Name:       openssh
Version:    10.5p1
Release:    1
Summary:    OpenSSH connectivity tools and server
License:    BSD
URL:        https://www.openssh.com/
Source0:    openssh-%{version}.tar.gz
Source1:    sshd_config
Source2:    sshd.service
Source3:    sshd-keygen.service
Source4:    ssh-gen-host-keys
Source5:    openssh.sysusers
Source6:    openssh.tmpfiles
Source7:    90-openssh.preset
Source8:    sshd.pam
Prefix:     /usr
Requires:   linux-pam
Requires:   systemd
BuildRequires: linux-pam

%description
OpenSSH is the premier connectivity tool for remote login with the SSH
protocol.  It encrypts all traffic to eliminate eavesdropping, connection
hijacking, and other attacks.  This package provides the client tools and
the sshd server, configured with Linux-PAM password authentication and
systemd units that generate host keys on first boot.

%prep
%setup

%build
%configure --sysconfdir=/etc/ssh                    \
           --sbindir=/usr/sbin                      \
           --with-privsep-path=/var/lib/sshd        \
           --with-default-path=/usr/bin             \
           --with-superuser-path=/usr/sbin:/usr/bin \
           --with-pid-dir=/run                      \
           --with-pam                               \
           --with-xauth=/usr/bin/xauth
%make_build

%install
rm -rf %{buildroot}
%make_install

# Install ssh-copy-id, which the upstream install target omits.
install -v -m755 contrib/ssh-copy-id %{buildroot}%{_bindir}/ssh-copy-id
install -v -m644 contrib/ssh-copy-id.1 %{buildroot}%{_mandir}/man1/ssh-copy-id.1

# Documentation.
install -vdm755 %{buildroot}%{_docdir}/openssh-%{version}
install -vm644 INSTALL LICENCE OVERVIEW README* \
    %{buildroot}%{_docdir}/openssh-%{version}/

# Our server configuration replaces the upstream sample.
install -vdm755 %{buildroot}/etc/ssh/sshd_config.d
install -vm644 %{SOURCE1} %{buildroot}/etc/ssh/sshd_config

# PAM service definition.
install -vdm755 %{buildroot}/etc/pam.d
install -vm644 %{SOURCE8} %{buildroot}/etc/pam.d/sshd

# systemd units, first-boot key generation, sysusers and tmpfiles.
install -vdm755 %{buildroot}%{_unitdir}
install -vm644 %{SOURCE2} %{buildroot}%{_unitdir}/sshd.service
install -vm644 %{SOURCE3} %{buildroot}%{_unitdir}/sshd-keygen.service
install -vdm755 %{buildroot}%{_bindir}
install -vm755 %{SOURCE4} %{buildroot}%{_bindir}/ssh-gen-host-keys

install -vdm755 %{buildroot}/usr/lib/sysusers.d
install -vm644 %{SOURCE5} %{buildroot}/usr/lib/sysusers.d/openssh.conf
install -vdm755 %{buildroot}/usr/lib/tmpfiles.d
install -vm644 %{SOURCE6} %{buildroot}/usr/lib/tmpfiles.d/openssh.conf
install -vdm755 %{buildroot}/usr/lib/systemd/system-preset
install -vm644 %{SOURCE7} \
    %{buildroot}/usr/lib/systemd/system-preset/90-openssh.preset

# PrivSep chroot directory.  OpenSSH requires the directory to be owned by
# root and not group/world-writable; sshd's group owns it and the mode is 0700.
# sysusers gives sshd uid/gid 50, so use numeric IDs here.
install -vdm700 %{buildroot}/var/lib/sshd
chown -v 0:50 %{buildroot}/var/lib/sshd

%post
# Make the package usable immediately when installed with scriptlets enabled.
if [ -x /usr/bin/systemd-sysusers ]; then
    /usr/bin/systemd-sysusers /usr/lib/sysusers.d/openssh.conf || :
fi
if [ -x /usr/bin/systemd-tmpfiles ]; then
    /usr/bin/systemd-tmpfiles --create /usr/lib/tmpfiles.d/openssh.conf || :
fi
install -d -m 0700 -o root -g sshd /var/lib/sshd 2>/dev/null || :

%files -f %{_sourcedir}/openssh.filelist
%attr(0700,root,sshd) %dir /var/lib/sshd

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 10.5p1-1
- Rewrite for BLFS r13.1 OpenSSH 10.5p1
- Linux-PAM password authentication (--with-pam, UsePAM yes,
  PermitRootLogin yes) and an /etc/pam.d/sshd pam_unix stack
- systemd sshd.service (Type=notify) + sshd-keygen.service and
  /usr/bin/ssh-gen-host-keys (rsa/ecdsa/ed25519, no DSA)
- sysusers/tmpfiles entries, /var/lib/sshd 0700, and a preset that enables
  sshd and sshd-keygen
- Remove the finit sshd service and the old make_sshd_keys helper

* Fri Jun 16 2023 Chris Statzer <chris.statzer@gmail.com> 8.0p1-5
- Renamed service destination file to follow the naming scheme

* Thu May 14 2020 Chris Statzer <chris.statzer@qq.com> 8.0p1
- Added finit services and a default configuration
