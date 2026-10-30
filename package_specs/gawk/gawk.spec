Name:       gawk
Version:    5.4.1
Release:    1
Summary:    GNU pattern scanner
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

Provides: /bin/gawk

%description
Gawk is a powerful text-processing and data-manipulating tool

%prep
%setup -q

%build
sed -i 's/extras//' Makefile.in
%configure 
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/awk
/usr/bin/gawk
/usr/bin/gawk-%{version}
/usr/bin/gawkbug
/usr/include/gawkapi.h
/usr/lib64/gawk/filefuncs.so
/usr/lib64/gawk/fnmatch.so
/usr/lib64/gawk/fork.so
/usr/lib64/gawk/inplace.so
/usr/lib64/gawk/intdiv.so
/usr/lib64/gawk/ordchr.so
/usr/lib64/gawk/readdir.so
/usr/lib64/gawk/readfile.so
/usr/lib64/gawk/revoutput.so
/usr/lib64/gawk/revtwoway.so
/usr/lib64/gawk/rwarray.so
/usr/lib64/gawk/time.so
/usr/libexec/awk/grcat
/usr/libexec/awk/pwcat
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/awk/
/usr/share/locale/
/usr/share/man/
/usr/share/info/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 5.4.1
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 5.2.2-1
- Version bump
