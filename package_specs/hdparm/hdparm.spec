Name:       hdparm
Version:    9.65
Release:    1
Summary:    Utility for displaying and setting hard disk parameters
License:    LicenseRef-hdparm
URL:        https://sourceforge.net/projects/hdparm/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: gcc
BuildRequires: make

%description
hdparm is a command-line utility to get and set IDE, SATA and SCSI hard
disk parameters, such as spin-down timeouts, write caching, DMA modes and
security settings.  TuneD's disk plugin uses it for the spindown-disk
profile.

%prep
%setup -q

%build
%make_build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} sbindir=/usr/sbin manprefix=/usr

%files -f %{_sourcedir}/hdparm.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 9.65-1
- New package: hdparm 9.65 (latest stable upstream).  Not in the base set;
  TuneD requires it and the disk plugin uses it for spindown-disk.
- The license is recorded as LicenseRef-hdparm: upstream ships a custom
  BSD-style license with a name-retention condition, which has no SPDX
  identifier.
