Name:       dosfstools
Version:    4.2
Release:    1
Summary:    dosfstools consists of the programs needed to create, check and label file systems of the FAT family. 
License:    GPL-3.0
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
dosfstools consists of the programs mkfs.fat, fsck.fat and fatlabel to create, check and label file systems of the FAT family. 

%prep
%setup -q

%build
%configure --sbindir=/usr/sbin --enable-compat-symlinks --docdir=/usr/share/doc/dosfstools-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/dosfstools.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.2-1
- Build the current BLFS r13.1 version (4.2)
- Configure with --enable-compat-symlinks as the book does, providing
  mkfs.vfat/mkfs.msdos/fsck.vfat/fsck.msdos for the installer
- Ship a generated static filelist
