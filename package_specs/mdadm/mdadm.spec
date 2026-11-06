Name:       mdadm
Version:    4.6
Release:    1
Summary:    Administrative tools for Linux software RAID arrays
License:    GPL-2.0-or-later
URL:        https://git.kernel.org/pub/scm/utils/mdadm/mdadm.git
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The mdadm package contains administration tools for software RAID: mdadm
to create, manage and monitor MD (Linux software RAID) devices, and mdmon
to monitor MD external metadata arrays.

%prep
%setup -q

%build
%make_build BINDIR=/usr/sbin

%install
rm -rf %{buildroot}
make install BINDIR=/usr/sbin DESTDIR=%{buildroot}
# A plain `make install` leaves the systemd units out; install
# them for the systemd-based Tenko system.
make install-systemd BINDIR=/usr/sbin SYSTEMD_DIR=%{_unitdir} \
     DESTDIR=%{buildroot}

%files -f %{_sourcedir}/mdadm.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.6-1
- New package at the pinned version (4.6).
- Built with the documented `make` / `make BINDIR=/usr/sbin install`
  procedure; the mdmon systemd units are installed as well.
