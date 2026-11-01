Name:       xz
Version:    5.8.4
Release:    1
Summary:    Free general-purpose data compression software
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
XZ Utils is free general-purpose data compression software with a high compression ratio. 

%prep
%setup -q

%build
./configure --prefix=/usr    \
            --disable-static \
            --docdir=/usr/share/doc/xz-%{version} \
            --libdir=%{_libdir}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xz.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 5.8.3
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 5.8.3
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 5.4.4
- Version bump
