Name:       sysklogd
Version:    2.8.0
Release:    1
Summary:    TODO
License:    GPL3
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
TODO

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

%files
/etc/syslog.conf
/usr/bin/syslogd
/usr/include/syslog/syslog.h
/usr/lib/systemd/system/syslogd.service
/usr/lib64/libsyslog.so
/usr/lib64/libsyslog.so.0
/usr/lib64/libsyslog.so.0.2.0
/usr/lib64/pkgconfig/libsyslog.pc
/usr/share/doc/sysklogd-2.8.0/ChangeLog.md
/usr/share/doc/sysklogd-2.8.0/LICENSE
/usr/share/doc/sysklogd-2.8.0/README.md
/usr/share/doc/sysklogd-2.8.0/example/README.md
/usr/share/doc/sysklogd-2.8.0/example/example.c
/usr/share/doc/sysklogd-2.8.0/example/example.mk
/usr/share/doc/sysklogd-2.8.0/syslog.conf
/usr/share/man/man3/syslogp.3.gz
/usr/share/man/man5/syslog.conf.5.gz
/usr/share/man/man8/syslogd.8.gz

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.8.0-1
- Sync with LFS r13.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.1-1
- Version bump

