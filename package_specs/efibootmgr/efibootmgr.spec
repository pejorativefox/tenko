Name:       efibootmgr
Version:    18
Release:    1
Summary:    The efibootmgr package provides tools and libraries to manipulate EFI variables.
License:    GPL-2.0
URL:        https://github.com/rhboot/efibootmgr
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: efivar
BuildRequires: gcc-lto

%description
This is efibootmgr, a Linux user-space application to modify the Intel Extensible Firmware Interface (EFI) Boot Manager. This application can create and destroy boot entries, change the boot order, change the next running boot option, and more.

%prep
%setup -q

%build
make EFIDIR=TENKO EFI_LOADER=grubx64.efi

%install
rm -rf %{buildroot}
%make_install EFIDIR=TENKO

%files -f %{_sourcedir}/efibootmgr.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 18-1
- Build the current pinned version (18)
- Install the man pages and binaries with the Tenko ESP directory (EFIDIR=TENKO)
- Ship a generated static filelist

