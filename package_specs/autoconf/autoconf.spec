Name:       autoconf
Version:    2.73
Release:    3
Summary:    Tool for producing configure scripts
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Autoconf is an extensible package of M4 macros that produce shell scripts to automatically configure software source code packages. 

%package doc
Summary:    autoconf documentation
Requires:   autoconf = %{version}-%{release}

%description doc
Documentation for autoconf.

%prep
%setup

%build
sed -e 's/SECONDS|/&SHLVL|/'               \
    -e '/BASH_ARGV=/a\        /^SHLVL=/ d' \
    -i.orig tests/local.at

%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/autoconf.filelist
%files doc -f %{_sourcedir}/autoconf-doc.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.73-3
- Record the verified license (GPL-3.0-or-later): README (GPLv3+) and COPYINGv3 (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.73-2
- Split doc payload into autoconf-doc (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.73
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 2.71-1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 2.69
- Initial RPM

