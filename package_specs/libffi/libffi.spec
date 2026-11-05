Name:       libffi
Version:    3.8.0
Release:    2
Summary:    Foreign Function Interface library
License:    MIT
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The Libffi library provides a portable, high level programming interface to various calling conventions. This allows a programmer to call any function specified by a call interface description at run time.

%prep
%setup -q

%build
%configure --disable-static --with-gcc-arch=native
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/include/ffi.h
/usr/include/ffitarget.h
/usr/lib64/libffi.so
/usr/lib64/libffi.so.8
/usr/lib64/libffi.so.8.5.0
/usr/lib64/pkgconfig/libffi.pc
/usr/share/info/libffi.info.gz
/usr/share/man/man3/ffi.3.gz
/usr/share/man/man3/ffi_call.3.gz
/usr/share/man/man3/ffi_prep_cif.3.gz
/usr/share/man/man3/ffi_prep_cif_var.3.gz


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.8.0-2
- Record the verified license (MIT): LICENSE (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.8.0
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump
