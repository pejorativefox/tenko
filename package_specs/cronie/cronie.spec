Name:       cronie
Version:    1.7.2
Release:    3
Summary:    The Vixie Cron daemon (crond) and the crontab command
License:    BSD-2-Clause AND ISC AND GPL-2.0-or-later
URL:        https://github.com/cronie-crond/cronie
Source0:    %{name}-%{version}.tar.gz
Source1:    crond.service
Source2:    cron.deny
Source3:    90-cronie.preset
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

# systemd unit, enabled by default through the preset.
install -vdm755 %{buildroot}%{_unitdir}
install -vm644 %{SOURCE1} %{buildroot}%{_unitdir}/crond.service
install -vdm755 %{buildroot}/usr/lib/systemd/system-preset
install -vm644 %{SOURCE3} %{buildroot}/usr/lib/systemd/system-preset/90-cronie.preset

# Ship an empty deny file: every user may use crontab.
cp %{SOURCE2} %{buildroot}/etc/cron.deny

%post
# Enable the daemon when the package is installed on a running system;
# the rootfs build enables it with systemctl preset-all.
if [ -x /usr/bin/systemctl ] && [ -d /run/systemd/system ]; then
    /usr/bin/systemctl preset crond.service || :
fi

%files -f %{_sourcedir}/cronie.filelist

%changelog
* Fri Nov 20 2026 tenko <build@tenko.invalid> 1.7.2-3
- Replace the finit service with a systemd unit (crond.service) plus a
  default-enable preset, matching the boot flow (systemd-boot,
  systemctl preset-all).  A %post presets the unit on running systems.

* Fri Nov 20 2026 tenko <build@tenko.invalid> 1.7.2-2
- Ship an empty /etc/cron.deny: with neither cron.allow nor cron.deny
  present, cronie only lets root use crontab (reported by the first
  `crontab -e` run).

* Fri Nov 20 2026 tenko <build@tenko.invalid> 1.7.2-1
- New package, added to the base set: latest upstream stable release
  (1.7.2, checked 2026-11-20).
