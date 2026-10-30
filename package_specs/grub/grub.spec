%global __global_ldflags %{nil}
%global _lto_cflags %{nil}

Name:       grub
Version:    2.14
Release:    1
Summary:    GNU GRUB is a Multiboot boot loader.
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr


%description
GNU GRUB is a Multiboot boot loader. It was derived from GRUB, the GRand Unified Bootloader, which was originally designed and implemented by Erich Stefan Boleyn.

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
mkdir -pv %{buildroot}/usr/share/bash-completion/completions
mv -v %{buildroot}/etc/bash_completion.d/grub %{buildroot}/usr/share/bash-completion/completions

%files
/etc/grub.d/
/usr/bin/grub-*
/usr/lib64/grub/x86_64-efi/
/usr/sbin/grub-bios-setup
/usr/sbin/grub-install
/usr/sbin/grub-macbless
/usr/sbin/grub-mkconfig
/usr/sbin/grub-ofpathname
/usr/sbin/grub-probe
/usr/sbin/grub-reboot
/usr/sbin/grub-set-default
/usr/sbin/grub-sparc64-setup
/usr/share/bash-completion/completions/grub
/usr/share/grub/grub-mkconfig_lib
/usr/share/info/
/usr/share/locale/ 

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.14
- Sync with LFS r13.1

* Tue Jun 13 2023 Chris Statzer <chris.statzer@gmail.com> 2.06-1
- Updating grub to allow a clean patch to fix a bug: https://wiki.linuxfromscratch.org/lfs/ticket/4354

* Tue Jun 13 2023 Chris Statzer <chris.statzer@gmail.com> 2.02-2
- Added UEFI support to build
