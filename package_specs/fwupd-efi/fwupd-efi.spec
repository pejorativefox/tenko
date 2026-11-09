Name:       fwupd-efi
Version:    1.9
Release:    1
Summary:    UEFI executable for installing firmware capsules with fwupd
License:    LGPL-2.1-or-later
URL:        https://github.com/fwupd/fwupd-efi
Source0:    %{name}-%{version}.tar.xz
BuildRequires: gnu-efi >= 3.0.18
BuildRequires: gcc
BuildRequires: binutils
BuildRequires: meson
BuildRequires: ninja
BuildRequires: python
BuildRequires: python-pefile
Prefix:     /usr

%description
fwupd-efi builds the small UEFI application that the fwupd daemon launches
to apply UEFI capsule updates through the UpdateCapsule runtime service.
It is installed under /usr/libexec/fwupd/efi and used by fwupd's
uefi-capsule plugin.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                              \
      --prefix=/usr                         \
      --buildtype=release                   \
      -Defi_sbat_distro_id=tenko            \
      -Defi_sbat_distro_summary="Tenko 6 Workstation" \
      -Defi_sbat_distro_pkgname=fwupd-efi   \
      -Defi_sbat_distro_version=%{version}-%{release} \
      -Defi_sbat_distro_url=https://tenko.pjfox.xyz/ \
      -Dgenpeimg=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
install -Dpm0644 COPYING %{buildroot}/usr/share/licenses/fwupd-efi/COPYING

%files -f %{_sourcedir}/fwupd-efi.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 1.9-1
- Initial package: latest stable upstream release 1.9, compatible with
  fwupd 2.1.9 and built against gnu-efi 3.0.18.
- Licence verified from COPYING and the SPDX headers in the EFI sources
  (LGPL-2.1-or-later).
- SBAT metadata identifies the binary as Tenko 6 Workstation.
