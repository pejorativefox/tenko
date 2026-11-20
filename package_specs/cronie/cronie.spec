Name:       cronie
Version:    1.7.2
Release:    1
Summary:    The Vixie Cron daemon (crond) and the crontab command
License:    BSD-2-Clause AND ISC AND GPL-2.0-or-later
URL:        https://github.com/cronie-crond/cronie
Source0:    %{name}-%{version}.tar.gz
Source1:    crond.conf
# GCC 16 defaults to C23: the load_entry error callback must be declared
# with a (const char *) parameter, not an empty () list.
Patch0:     %{name}-%{version}-c23-error-callback.patch
Prefix:     /usr

BuildRequires: linux-pam

%description
Cronie contains the standard UNIX daemon crond that runs specified
programs at scheduled times and related tools: the crontab command for
editing user crontabs and anacron for jobs on machines that are not
always up.  It is a fork of the original vixie-cron.

%prep
%setup -q
%patch -P 0 -p1

%build
# Pin the paths the daemon is compiled with, and run as root: no dedicated
# user or group is needed.  PAM gives session limits (pam_limits) and
# ships /etc/pam.d/crond; audit and SELinux are optional and not built.
%configure \
    --sysconfdir=/etc \
    --localstatedir=/var \
    --with-daemon_username=root \
    --with-daemon_groupname=root \
    --with-inotify \
    --with-pam \
    --with-editor=/usr/bin/vi
%make_build

%install
rm -rf %{buildroot}
%make_install

# crontab needs setuid root to install user crontabs in the spool.
chmod 4755 %{buildroot}%{_bindir}/crontab

# Directories the daemon and crontab expect; not installed by make.
mkdir -pv %{buildroot}/etc/cron.d
mkdir -pv %{buildroot}/var/spool/cron
chmod 700 %{buildroot}/var/spool/cron

# finit service: crond -n stays in the foreground.
mkdir -pv %{buildroot}/etc/finit.d/available
cp %{SOURCE1} %{buildroot}/etc/finit.d/available/crond.conf

%files -f %{_sourcedir}/cronie.filelist

%changelog
* Fri Nov 20 2026 tenko <build@tenko.invalid> 1.7.2-1
- New package, added to the base set: latest upstream stable release
  (1.7.2, checked 2026-11-20).
