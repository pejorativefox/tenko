Name:       virt-what
Version:    1.27
Release:    1
Summary:    Detect if we are running in a virtual machine
License:    GPL-2.0-or-later
URL:        https://people.redhat.com/~rjones/virt-what/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: gcc
BuildRequires: make
Requires:   dmidecode
Requires:   util-linux
Requires:   which

%description
virt-what is a shell script that detects whether the system is running in
a virtual machine and, if so, which kind of virtualisation is in use.  TuneD
requires it for the virtual-guest and virtual-host profiles.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/virt-what.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 1.27-1
- New package: virt-what 1.27 (latest stable upstream).  Not in the base
  set; TuneD requires it for virtual-guest and virtual-host detection.
