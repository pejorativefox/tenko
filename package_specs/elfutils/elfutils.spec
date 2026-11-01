Name:       elfutils
Version:    0.196
Release:    2
Summary:    ELF file handling library
License:    GPL3
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Libelf is a library for handling ELF (Executable and Linkable Format) files. 

%package devel
Summary:    elfutils development files
Requires:   elfutils = %{version}-%{release}

%description devel
Development files for elfutils.

%prep
%setup -q

%build
%configure  --disable-debuginfod         \
            --enable-libdebuginfod=dummy
%make_build

%install
rm -rf %{buildroot}
%make_install -C libelf
rm -vf %{buildroot}%{_infodir}/dir*
mkdir %{buildroot}/usr/lib64/pkgconfig/
install -vm644 config/libelf.pc %{buildroot}/usr/lib64/pkgconfig/
rm %{buildroot}/usr/lib64/libelf.a

%files -f %{_sourcedir}/elfutils.filelist
%files devel -f %{_sourcedir}/elfutils-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.196-2
- Split devel payload into elfutils-devel (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 0.195
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 0.189-1
- Version bump
