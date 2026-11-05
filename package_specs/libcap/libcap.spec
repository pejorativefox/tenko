Name:       libcap
Version:    2.78
Release:    3
Summary:    POSIX 1003.1e capabilities
License:    BSD-3-Clause OR GPL-2.0-only
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

Provides: libcap.so.2()(64bit)

%description
POSIX 1003.1e capabilities

%prep
%setup -q 

%build
sed -i '/install -m.*STA/d' libcap/Makefile
%make_build

%install    
rm -rf %{buildroot}
%make_install prefix=/usr
	
%files
/usr/include/sys/capability.h
/usr/include/sys/psx_syscall.h
/usr/lib64/libcap.so
/usr/lib64/libcap.so.2
/usr/lib64/libcap.so.2.78
/usr/lib64/libpsx.so
/usr/lib64/libpsx.so.2
/usr/lib64/libpsx.so.2.78
/usr/lib64/pkgconfig/libcap.pc
/usr/lib64/pkgconfig/libpsx.pc
/usr/sbin/capsh
/usr/sbin/getcap
/usr/sbin/getpcaps
/usr/sbin/setcap
/usr/share/man/
/usr/lib64/security/pam_cap.so

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.78-3
- Replace the legacy short licence name with the verified SPDX expression
  (BSD-3-Clause OR GPL-2.0-only): the SPDX header in License (issue #8).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.78-2
- Ship pam_cap.so: with linux-pam-devel present, libcap's Makefile builds
  the PAM module (LFS builds libcap before linux-pam and so does not).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.78
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump
