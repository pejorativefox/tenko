%global __global_ldflags %{nil}
%global _lto_cflags %{nil}

Name:       grub
Version:    2.16
Release:    1
Summary:    GNU GRUB is a Multiboot boot loader.
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr


%description
GNU GRUB is a Multiboot boot loader. It was derived from GRUB, the GRand Unified Bootloader, which was originally designed and implemented by Erich Stefan Boleyn.

%package lang
Summary:    grub translations
Requires:   grub = %{version}-%{release}

%description lang
Translations for grub.

%prep
%setup -q -a0

%build
export LDFLAGS=""
export CFLAGS="-O2 -g"
export CXXFLAGS="-O2 -g"

%configure  --prefix=/usr        \
            --sysconfdir=/etc    \
            --disable-efiemu     \
            --with-platform=efi  \
            --target=x86_64      \
            --disable-werror

%make_build LDFLAGS=""

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/grub.filelist
%files lang -f %{_sourcedir}/grub-lang.filelist


%changelog
* Mon Nov  2 2026 browneye <build@browneye.invalid> 2.16-1
- Update to 2.16 (current LFS/BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.14-2
- Split lang payload into grub-lang (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.14
- Sync with LFS r13.1

* Tue Jun 13 2023 Chris Statzer <chris.statzer@gmail.com> 2.06-1
- Updating grub to allow a clean patch to fix a bug: https://wiki.linuxfromscratch.org/lfs/ticket/4354

* Tue Jun 13 2023 Chris Statzer <chris.statzer@gmail.com> 2.02-2
- Added UEFI support to build
