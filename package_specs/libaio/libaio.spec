Name:       libaio
Version:    0.3.113
Release:    1
Summary:    Linux-native asynchronous I/O facility
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
libaio provides the Linux-native API for asynchronous I/O, used by LVM2 and
other storage tools.

%prep
%setup -q

%build
# BLFS: do not install the static library.
sed -i '/install.*libaio.a/s/^/#/' src/Makefile
%make_build

%install
rm -rf %{buildroot}
%make_install prefix=%{_prefix} libdir=%{_libdir}

%files
/usr/include/libaio.h
/usr/lib64/libaio.so
/usr/lib64/libaio.so.1
/usr/lib64/libaio.so.1.0.2

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.3.113-1
- Update to the BLFS r13.1 version (0.3.113, was 0.3.112) for LVM2 2.03.42
- Install into /usr/lib64 (the Makefile defaults to /usr/lib)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.3.112
- Initial RPM
