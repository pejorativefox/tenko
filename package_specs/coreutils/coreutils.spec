Name:       coreutils
Version:    9.11
Release:    1
Summary:    GNU operating system tools
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Patch:      coreutils-8.30-i18n-1.patch
Prefix:     /usr

%description
The GNU Core Utilities are the basic file, shell and text manipulation utilities of the GNU operating system.

%prep
%setup -q
patch -Np1 -i %{_sourcedir}/coreutils-9.11-i18n-1.patch

%build

export FORCE_UNSAFE_CONFIGURE=1  
%configure --enable-no-install-program=kill,uptime
%make_build 
unset FORCE_UNSAFE_CONFIGURE

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/
/usr/libexec/coreutils/
/usr/share/info/
/usr/share/locale/
/usr/share/man/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 9.11
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 9.3-1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 8.30-1
- Initial RPM
