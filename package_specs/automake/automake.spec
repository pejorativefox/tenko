Name:       automake
Version:    1.18.1
Release:    1
Summary:    Tool for producing inputs for autoconf
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
GNU Automake is a tool for automatically generating Makefile.in files compliant with the GNU Coding Standards. Automake requires the use of GNU Autoconf. 

%prep
%setup

%build
%configure --docdir=/usr/share/doc/automake-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/aclocal
/usr/bin/aclocal-1.18
/usr/bin/automake
/usr/bin/automake-1.18
/usr/share/aclocal/README
/usr/share/aclocal-1.18/
/usr/share/automake-1.18/
/usr/share/doc/automake-%{version}/amhello-1.0.tar.gz
/usr/share/info/automake-history.info.gz
/usr/share/info/automake.info-1.gz
/usr/share/info/automake.info-2.gz
/usr/share/info/automake.info.gz
/usr/share/man/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.18.1
- Sync with LFS r13.1

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.18.1
- Initial RPM
