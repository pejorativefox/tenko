Name:       linux-pam
Version:    1.7.3
Release:    5
Summary:    PAM (Pluggable Authentication Modules) library
License:    BSD-3-Clause OR GPL-2.0-or-later
URL:        https://github.com/linux-pam/linux-pam
Source0:    Linux-PAM-%{version}.tar.xz
Source1:    Linux-PAM-%{version}-docs.tar.xz
Prefix:     /usr
BuildRequires: meson
BuildRequires: ninja

%description
Linux-PAM (Pluggable Authentication Modules) is a suite of shared
libraries and modules that provide a flexible, modular authentication
mechanism for applications.  It is used by sshd, systemd-logind, and
other system services.

%package lang
Summary:    linux-pam translations
Requires:   linux-pam = %{version}-%{release}

%description lang
Translations for linux-pam.

%package doc
Summary:    linux-pam documentation
Requires:   linux-pam = %{version}-%{release}

%description doc
Documentation for linux-pam.

%prep
%setup -n Linux-PAM-%{version}

%build
mkdir -p build
pushd build
meson setup ..                  \
      --prefix=/usr             \
      --buildtype=release       \
      --wrap-mode=nofallback    \
      -D docs=disabled          \
      -D examples=false         \
      -D selinux=disabled       \
      -D docdir=/usr/share/doc/Linux-PAM-%{version}
ninja -j8
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

# unix_chkpwd is setgid shadow so pam_unix can verify passwords for
# unprivileged callers (screen lockers, PAM-aware login programs).
chmod 4755 %{buildroot}/usr/sbin/unix_chkpwd

# Pre-built man pages and guides ship with the package; the base does not
# have the DocBook toolchain needed to generate them.
tar -C %{buildroot} --no-same-owner --skip-old-files \
    -xJf %{SOURCE1}

# The default PAM stack.  Applications (including sshd) include or
# duplicate these; the restrictive "other" entry keeps unknown services
# from silently falling through to an allow-all stack.
install -vdm755 %{buildroot}/etc/pam.d

cat > %{buildroot}/etc/pam.d/system-account <<'EOF'
# Begin /etc/pam.d/system-account

account   required    pam_unix.so

# End /etc/pam.d/system-account
EOF

cat > %{buildroot}/etc/pam.d/system-auth <<'EOF'
# Begin /etc/pam.d/system-auth

auth      required    pam_unix.so

# End /etc/pam.d/system-auth
EOF

cat > %{buildroot}/etc/pam.d/system-session <<'EOF'
# Begin /etc/pam.d/system-session

session   required    pam_unix.so

# Begin Systemd addition
session   required    pam_loginuid.so
session   optional    pam_systemd.so
# End Systemd addition

# End /etc/pam.d/system-session
EOF

cat > %{buildroot}/etc/pam.d/system-password <<'EOF'
# Begin /etc/pam.d/system-password

# yescrypt is the libxcrypt default used by Tenko's shadow build.
password  required    pam_unix.so       yescrypt shadow try_first_pass

# End /etc/pam.d/system-password
EOF

cat > %{buildroot}/etc/pam.d/other <<'EOF'
# Begin /etc/pam.d/other

auth        required        pam_warn.so
auth        required        pam_deny.so
account     required        pam_warn.so
account     required        pam_deny.so
password    required        pam_warn.so
password    required        pam_deny.so
session     required        pam_warn.so
session     required        pam_deny.so

# End /etc/pam.d/other
EOF

# Service files for the PAM-aware programs the base system ships.  Without
# them every one of the shadow utilities (login, su, passwd, ...) falls
# back to the deny-all "other" stack, so console logins and password
# changes fail.  Found by the installer boot test: chpasswd could not set
# the admin password.  They use this distro's split stacks (system-auth has
# the auth stack only, passwords live in system-password).

cat > %{buildroot}/etc/pam.d/login <<'EOF'
# Begin /etc/pam.d/login

auth        include     system-auth
account     include     system-account
password    include     system-password
session     include     system-session

# End /etc/pam.d/login
EOF

cat > %{buildroot}/etc/pam.d/su <<'EOF'
# Begin /etc/pam.d/su

auth        sufficient  pam_rootok.so
auth        include     system-auth
account     include     system-account
session     include     system-session

# End /etc/pam.d/su
EOF

cat > %{buildroot}/etc/pam.d/passwd <<'EOF'
# Begin /etc/pam.d/passwd

auth        include     system-auth
account     include     system-account
password    include     system-password

# End /etc/pam.d/passwd
EOF

for service in chpasswd newusers; do
cat > %{buildroot}/etc/pam.d/$service <<'EOF'
# Begin /etc/pam.d/@SERVICE@

auth        sufficient  pam_rootok.so
account     required    pam_permit.so
password    include     system-password

# End /etc/pam.d/@SERVICE@
EOF
sed -i "s/@SERVICE@/$service/" %{buildroot}/etc/pam.d/$service
done

%files -f %{_sourcedir}/linux-pam.filelist
%files lang -f %{_sourcedir}/linux-pam-lang.filelist
%files doc -f %{_sourcedir}/linux-pam-doc.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.7.3-5
- Add systemd lines to system-session: pam_loginuid and
  pam_systemd.  Without pam_systemd, console/tty logins (login, su)
  did not register a logind session even though GUI logins through
  LightDM did (issue #7).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.7.3-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.7.3-3
- Ship PAM service files for the shadow utilities: login, su, passwd,
  chpasswd and newusers.  Without them the PAM-enabled login/su/passwd/
  chpasswd fell through to the deny-all "other" stack, so console logins
  failed and the installer could not set the admin password
  (pam_chauthtok: Authentication token manipulation error).  Found by the
  first unattended installer test.
- The files use this distro's split stacks: system-auth holds the auth
  stack, system-password the password stack.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.7.3-2
- Split lang, doc, devel payload into linux-pam-lang, linux-pam-doc, linux-pam-devel (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.7.3-1
- Update to Linux-PAM 1.7.3 (meson build)
- Install PAM modules in /usr/lib64/security and default
  /etc/pam.d stack (system-auth/account/password/session + other)
- Ship pre-built man pages and documentation

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.3.0
- Initial RPM
