Name:       smartmontools
Version:    7.5
Release:    1
Summary:    Tools for monitoring SMART status of ATA/SATA/SCSI/NVMe disks
License:    GPL-2.0-or-later
URL:        https://www.smartmontools.org/
Source0:    %{name}-%{version}.tar.gz
Source1:    %{name}.sysconfig
Prefix:     /usr

Requires:   curl
Recommends: gnupg

BuildRequires: gcc
BuildRequires: make
BuildRequires: libcap-ng
BuildRequires: systemd

%description
The smartmontools package contains smartctl and smartd.  smartctl controls
and monitors the S.M.A.R.T. self-monitoring, analysis and reporting
technology built into ATA/SATA, SCSI/SAS and NVMe disks: it reports health
status, temperature, power-on hours, error logs and self-test results.
smartd is the background daemon that polls the configured devices and can
run scripts or send mail when a disk reports a problem.

smartmontools is not part of the base set; it is an optional disk-health
tool.  The smartd service is installed but not enabled by default.  The
update-smart-drivedb helper needs curl; GnuPG signature verification is
recommended and pulls gnupg when weak dependencies are installed.

%prep
%setup -q

%build
%configure \
    --with-libcap-ng=yes \
    --with-libsystemd=yes \
    --with-systemdsystemunitdir=%{_unitdir} \
    --with-systemdenvfile=/etc/sysconfig/smartmontools \
    --with-savestates=yes \
    --with-attributelog=yes \
    --with-update-smart-drivedb=yes
%make_build

%install
rm -rf %{buildroot}
%make_install
install -Dpm0644 %{_sourcedir}/%{name}.sysconfig \
    %{buildroot}/etc/sysconfig/smartmontools

%post
if [ -x /usr/bin/systemctl ]; then
    systemctl daemon-reload >/dev/null 2>&1 || :
fi

%postun
if [ -x /usr/bin/systemctl ]; then
    systemctl daemon-reload >/dev/null 2>&1 || :
fi

%files -f %{_sourcedir}/smartmontools.filelist

%changelog
* Fri Nov 13 2026 tenko <build@tenko.invalid> 7.5-1
- New package: smartmontools 7.5 (latest stable upstream, checked
  2026-11-13).  Not in the base set.
- Built with libcap-ng and libsystemd (smartd Type=notify), the systemd
  unit and /etc/sysconfig/smartmontools are installed, and smartd is left
  disabled.  smartd state and attribute logs live under
  /var/lib/smartmontools.
- curl is a runtime requirement of the shipped update-smart-drivedb
  helper; gnupg is recommended for its signature check.
