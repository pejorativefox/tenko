Name:       mtools
Version:    4.0.50
Release:    1
Summary:    Utilities to access MS-DOS disks from GNU and Unix without mounting them
License:    GPL-3.0-or-later
URL:        https://www.gnu.org/software/mtools/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Mtools is a collection of utilities to access MS-DOS disks (FAT filesystems)
from GNU and Unix without mounting them.  The Tenko UEFI installer uses
mcopy/mmd to populate the FAT EFI system partition of the hybrid ISO.

This package is a user-approved exception to the base-set version policy
rule: mtools is not in the base set, so it tracks current upstream.
Source: https://ftp.gnu.org/gnu/mtools/mtools-4.0.50.tar.gz
sha256: 7f078accae7551c6b3a316ccd8296357329f7bbbc09583dcd1a2bbaeb081a7a4

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/mtools.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.0.50-1
- Update to upstream 4.0.50 (approved exception; not in the base set), replacing
  the 4.0.43 template.  Recorded source sha256:
  7f078accae7551c6b3a316ccd8296357329f7bbbc09583dcd1a2bbaeb081a7a4

* Tue Jun 13 2023 Chris Statzer <chris.statzer@gmail.com> 3.30.1
- Initial RPM
