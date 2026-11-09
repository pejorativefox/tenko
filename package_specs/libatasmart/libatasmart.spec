Name:       libatasmart
Version:    0.19
Release:    1
Summary:    ATA S.M.A.R.T. disk health monitoring library
License:    LGPL-2.1-or-later
URL:        https://0pointer.de/blog/projects/being-smart.html
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
libatasmart reads and parses ATA S.M.A.R.T. data from hard disks and
solid-state drives.  It reports disk health, temperature, power-on hours and
the individual S.M.A.R.T. attributes.  The libblockdev smart plugin uses it
for udisks2 drive health reporting.

%prep
%setup -q

%build
%configure --disable-static --disable-rpath
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libatasmart.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 0.19-1
- Initial package at the latest stable upstream release, 0.19; upstream
  has no newer release.
- Verified the licence as LGPL-2.1-or-later from the LGPL licence text
  and the source file headers.
