Name:       dmidecode
Version:    3.7
Release:    1
Summary:    Tool to analyse BIOS DMI data
License:    GPL-2.0-or-later
URL:        https://www.nongnu.org/dmidecode/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: gcc
BuildRequires: make
BuildRequires: bash-completion

%description
dmidecode reports BIOS, system, baseboard, chassis, processor, memory,
cache and connector information from the SMBIOS/DMI tables.  TuneD uses it
for hardware detection and virtualisation checks, and virt-what requires it.

%prep
%setup -q

%build
%make_build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} prefix=/usr sbindir=/usr/sbin \
    mandir=/usr/share/man docdir=/usr/share/doc/dmidecode \
    compdir=/usr/share/bash-completion/completions

%files -f %{_sourcedir}/dmidecode.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 3.7-1
- New package: dmidecode 3.7 (latest stable upstream).  Not in the base set;
  virt-what requires it and TuneD uses it for hardware detection.
