Name:       zlib
Version:    1.3.2
Release:    2
Summary:    zlib compression library
License:    Zlib
URL:        https://zlib.net/
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

%files -f %{_sourcedir}/zlib.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.3.2-2
- Record the verified license (Zlib): LICENSE (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.3.2
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.13
- Version bump
