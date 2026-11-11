Name:       sysklogd
Version:    2.8.0
Release:    2
Summary:    System and kernel logging daemons
License:    BSD-3-Clause
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
This is the continuation of the original Debian/Ubuntu syslog daemon,
updated with full RFC 3164 and RFC 5424 support from NetBSD and FreeBSD. The
package includes the libsyslog library with a syslog.h header replacement,
the syslogd daemon and the logger command line tool.

%prep
%setup -q

%build
%configure --sysconfdir=/etc      \
           --runstatedir=/run     \
           --without-logger       \
           --disable-static       \
           --docdir=/usr/share/doc/sysklogd-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
mkdir -p %{buildroot}/etc

cat > %{buildroot}/etc/syslog.conf << "EOF"
# Begin /etc/syslog.conf

auth,authpriv.* -/var/log/auth.log
*.*;auth,authpriv.none -/var/log/sys.log
daemon.* -/var/log/daemon.log
kern.* -/var/log/kern.log
mail.* -/var/log/mail.log
user.* -/var/log/user.log
*.emerg *

# Do not open any internet ports.
secure_mode 2

# End /etc/syslog.conf
EOF

%files -f %{_sourcedir}/sysklogd.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.8.0-2
- Replace the TODO summary/description and record the verified license
  (BSD-3-Clause): LICENSE (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.8.0-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.1-1
- Version bump

