Name:       zlib
Version:    1.3.2
Release:    2
Summary:    zlib compression library
License:    Zlib
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The zlib compression library.

%prep
%setup -q -a0

%build
./configure --prefix=/usr --libdir=%{_libdir}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -fv %{buildroot}/usr/lib64/libz.a

%files
/usr/include/zconf.h
/usr/include/zlib.h
/usr/lib64/libz.so
/usr/lib64/libz.so.1
/usr/lib64/libz.so.1.3.2
/usr/lib64/pkgconfig/zlib.pc
/usr/share/man/man3/zlib.3.gz


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.3.2-2
- Record the verified license (Zlib): LICENSE (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.3.2
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.13
- Version bump
