Name:       automake
Version:    1.19
Release:    2
Summary:    Tool for producing inputs for autoconf
License:    GPL-2.0-or-later
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
/usr/bin/aclocal-1.19
/usr/bin/automake
/usr/bin/automake-1.19
/usr/share/aclocal/README
/usr/share/aclocal-1.19/
/usr/share/automake-1.19/
/usr/share/doc/automake-%{version}/amhello-1.0.tar.gz
/usr/share/info/automake-history.info.gz
/usr/share/info/automake.info-1.gz
/usr/share/info/automake.info-2.gz
/usr/share/info/automake.info.gz
/usr/share/man/

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.19-2
- Record the verified license (GPL-2.0-or-later): configure.ac and README (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.19.1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.19.1
- Initial RPM
