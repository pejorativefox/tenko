Name:       zstd
Version:    1.5.7
Release:    1
Summary:    Fast real-time compression algorith
License:    BSD
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Fast real-time compression algorith

%prep
%setup

%build
make prefix=/usr

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} prefix=/usr libdir=%{_libdir} install
rm -v %{buildroot}/usr/lib64/libzstd.a

%files
/usr/bin/unzstd
/usr/bin/zstd
/usr/bin/zstdcat
/usr/bin/zstdgrep
/usr/bin/zstdless
/usr/bin/zstdmt
/usr/include/zdict.h
/usr/include/zstd.h
/usr/include/zstd_errors.h
/usr/lib64/libzstd.so
/usr/lib64/libzstd.so.1
/usr/lib64/libzstd.so.1.5.7
/usr/lib64/pkgconfig/libzstd.pc
/usr/share/man/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.5.7
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.5
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.4.4
- Initial RPM

