Name:       sudo
Version:    1.9.17p2
Release:    2
Summary:    Execute commands as another user
License:    ISC
URL:        https://www.sudo.ws/
Source0:    %{name}-%{version}.tar.gz
Source1:    sudoers
Source2:    sudo.pam
Prefix:     /usr

BuildRequires: linux-pam
BuildRequires: openssl
Requires:   linux-pam

%description
Sudo (su "do") allows a system administrator to delegate authority to
give certain users (or groups of users) the ability to run some (or all)
commands as root or another user while logging the commands and their
arguments.  This build uses Linux-PAM for authentication.

%prep
%setup -q

# Fix building sudo with OpenSSL 4.
sed -e 's/\([->.a-zA-Z_]*\)->length/ASN1_STRING_length(\1)/' \
    -i lib/iolog/hostcheck.c

%build
%configure --prefix=/usr                                      \
           --libexecdir=/usr/lib                              \
           --with-secure-path                                 \
           --with-env-editor                                  \
           --with-pam                                         \
           --docdir=/usr/share/doc/sudo-%{version}            \
           --with-passprompt="[sudo] password for %p: "
%make_build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} \
     install_uid=0 install_gid=0 sudoers_uid=0 sudoers_gid=0

# Ship the Tenko sudoers policy instead of the upstream sample.
install -vdm755 %{buildroot}/etc/sudoers.d
install -vm0440 %{SOURCE1} %{buildroot}/etc/sudoers
chmod 0750 %{buildroot}/etc/sudoers.d

# Linux-PAM service definition for sudo.
install -vdm755 %{buildroot}/etc/pam.d
install -vm644 %{SOURCE2} %{buildroot}/etc/pam.d/sudo

# /run is created by tmpfiles at boot, not owned by the package.
rm -rf %{buildroot}/run

%pre
# The base system does not create a wheel group.  Create it so the
# %wheel rule in /etc/sudoers has a group to refer to; the installer is
# responsible for adding the administrative user to it.
if ! getent group wheel >/dev/null 2>&1; then
    groupadd -r wheel 2>/dev/null || :
fi

%files -f %{_sourcedir}/sudo.filelist
%attr(0440,root,root) %config(noreplace) /etc/sudoers
%attr(0440,root,root) %config(noreplace) /etc/sudoers.dist
%attr(0750,root,root) %dir /etc/sudoers.d
%attr(0644,root,root) %config(noreplace) /etc/pam.d/sudo
%config(noreplace) /etc/sudo.conf
%config(noreplace) /etc/sudo_logsrvd.conf

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.9.17p2-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.9.17p2-1
- Rewrite for sudo 1.9.17p2 (was a stale 1.8.23 template)
- Build with Linux-PAM; ship /etc/pam.d/sudo stack and an
  /etc/sudoers that grants %wheel ALL=(ALL) ALL with env_reset
- Split the plugin header into sudo-devel
- Create the wheel group in %%pre if the base system lacks it
