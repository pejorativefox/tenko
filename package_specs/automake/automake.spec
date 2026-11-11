Name:       automake
Version:    1.19
Release:    2
Summary:    Tool for producing inputs for autoconf
License:    GPL-2.0-or-later
URL:        https://www.gnu.org/software/automake/
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

%files -f %{_sourcedir}/automake.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.19-2
- Record the verified license (GPL-2.0-or-later): configure.ac and README (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.19.1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.19.1
- Initial RPM
