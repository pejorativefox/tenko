Name:       zstd
Version:    1.5.7
Release:    2
Summary:    Fast real-time compression algorith
License:    BSD-3-Clause OR GPL-2.0-only
URL:        https://facebook.github.io/zstd/
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

%files -f %{_sourcedir}/zstd.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.5.7-2
- Replace the legacy short licence name with the verified SPDX expression
  (BSD-3-Clause OR GPL-2.0-only): LICENSE (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.5.7
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.5
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.4.4
- Initial RPM

