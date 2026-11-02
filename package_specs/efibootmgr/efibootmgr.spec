Name:       efibootmgr
Version:    18
Release:    1
Summary:    The efibootmgr package provides tools and libraries to manipulate EFI variables.
License:    GPL-2.0
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
This is efibootmgr, a Linux user-space application to modify the Intel Extensible Firmware Interface (EFI) Boot Manager. This application can create and destroy boot entries, change the boot order, change the next running boot option, and more.

%prep
%setup -q

%build
make EFIDIR=LFS EFI_LOADER=grubx64.efi

%install
rm -rf %{buildroot}
%make_install EFIDIR=LFS

%files -f %{_sourcedir}/efibootmgr.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 18-1
- Build the current BLFS r13.1 version (18)
- Install the man pages and binaries as the book does (EFIDIR=LFS)
- Ship a generated static filelist

