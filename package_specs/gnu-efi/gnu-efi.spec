Name:       gnu-efi
Version:    3.0.18
Release:    1
Summary:    EFI development toolkit for building UEFI applications
License:    BSD-2-Clause AND BSD-2-Clause-Patent AND (GPL-2.0-or-later OR BSD-2-Clause) AND (GPL-2.0-or-later OR BSD-3-Clause)
URL:        https://sourceforge.net/projects/gnu-efi/
Source0:    %{name}-%{version}.tar.bz2
BuildRequires: gcc
BuildRequires: make
BuildRequires: binutils
Prefix:     /usr

%description
GNU-EFI provides the headers, static libraries, linker scripts and
pkg-config metadata needed to build UEFI applications and drivers with the
GNU toolchain.  fwupd-efi uses it to build the UEFI executable that installs
firmware capsules.

%prep
%setup -q

%build
# Only the library, relocator and header subtrees are needed.  The example
# applications under apps/ are not built or packaged.
make %{?_smp_mflags} PREFIX=/usr LIBDIR=/usr/lib64 lib gnuefi inc

%install
rm -rf %{buildroot}
arch=$(gcc -dumpmachine | cut -f1 -d-)
mkdir -p %{buildroot}/usr/lib64/pkgconfig
mkdir -p %{buildroot}/usr/include/efi/protocol
mkdir -p %{buildroot}/usr/include/efi/$arch
install -m644 $arch/lib/libefi.a %{buildroot}/usr/lib64/
install -m644 $arch/gnuefi/crt0-efi-$arch.o \
               $arch/gnuefi/libgnuefi.a \
               gnuefi/elf_${arch}_efi.lds \
               %{buildroot}/usr/lib64/
install -m644 $arch/gnuefi/gnu-efi.pc %{buildroot}/usr/lib64/pkgconfig/
install -m644 inc/*.h %{buildroot}/usr/include/efi/
install -m644 inc/protocol/*.h %{buildroot}/usr/include/efi/protocol/
install -m644 inc/$arch/*.h %{buildroot}/usr/include/efi/$arch/
install -Dpm0644 README.gnuefi \
    %{buildroot}/usr/share/doc/gnu-efi/README.gnuefi

%files -f %{_sourcedir}/gnu-efi.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 3.0.18-1
- Initial package: latest stable upstream release 3.0.18, the minimum
  version required by fwupd-efi 1.9 (pkg-config gnu-efi >= 3.0.18).
- Licence verified from the source headers: the bulk of the tree carries
  the BSD-2-Clause notice; individual files add BSD-2-Clause-Patent and
  dual GPL-2.0-or-later OR BSD-2-Clause / BSD-3-Clause terms, reflected in
  the SPDX expression above.
