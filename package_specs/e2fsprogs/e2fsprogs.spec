Name:       e2fsprogs
Version:    1.47.4
Release:    2
Summary:    ext filesystem utilities
License:    GPL3
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The E2fsprogs package contains the utilities for handling the ext2 file system. It also supports the ext3 and ext4 journaling file systems. 

%package lang
Summary:    e2fsprogs translations
Requires:   e2fsprogs = %{version}-%{release}

%description lang
Translations for e2fsprogs.

%package static
Summary:    e2fsprogs static libraries
Requires:   e2fsprogs = %{version}-%{release}

%description static
Static libraries for e2fsprogs.

%package devel
Summary:    e2fsprogs development files
Requires:   e2fsprogs = %{version}-%{release}

%description devel
Development files for e2fsprogs.

%prep
%setup -q

%build
mkdir -pv build
pushd build
../configure --prefix=/usr           \
             --libdir=%{_libdir}     \
             --enable-elf-shlibs     \
             --disable-libblkid      \
             --disable-libuuid       \
             --disable-uuidd         \
             --disable-fsck
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
%make_install
rm -fv %{buildroot}/usr/lib/{libcom_err,libe2p,libext2fs,libss}.a
popd

rm -vf %{buildroot}%{_infodir}/dir*
chmod +w %{buildroot}/usr/lib64/*.a

%files -f %{_sourcedir}/e2fsprogs.filelist
%files lang -f %{_sourcedir}/e2fsprogs-lang.filelist
%files static -f %{_sourcedir}/e2fsprogs-static.filelist
%files devel -f %{_sourcedir}/e2fsprogs-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.47.4-2
- Split lang, static, devel payload into e2fsprogs-lang, e2fsprogs-static, e2fsprogs-devel (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.47.4
- Sync with LFS r13.1

# let's skip this for now
