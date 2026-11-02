Name:       less
Version:    710
Release:    1
Summary:    open-source file pager. 
License:    GPL3
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Less is a free, open-source file pager. 

%prep
%setup -q

%build

%configure 
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/less
/usr/libexec/lessecho
/usr/libexec/less-osc8-open
/usr/share/man/man1/less.1.gz
/usr/share/man/man1/lessecho.1.gz
/usr/share/man/man5/lesskey.5.gz

%changelog
* Mon Nov  2 2026 browneye <build@browneye.invalid> 710-1
- Update to 710 (current LFS/BLFS r13.1 trunk version).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 704
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 643-1
 Version bump
