Name:       coreutils
Version:    9.11
Release:    2
Summary:    GNU operating system tools
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Patch:      coreutils-8.30-i18n-1.patch
Prefix:     /usr

%description
The GNU Core Utilities are the basic file, shell and text manipulation utilities of the GNU operating system.

%package lang
Summary:    coreutils translations
Requires:   coreutils = %{version}-%{release}

%description lang
Translations for coreutils.

%prep
%setup -q
patch -Np1 -i %{_sourcedir}/coreutils-9.11-i18n-1.patch

%build

export FORCE_UNSAFE_CONFIGURE=1  
%configure --enable-no-install-program=kill,uptime --without-selinux --without-openssl
%make_build 
unset FORCE_UNSAFE_CONFIGURE

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/coreutils.filelist
%files lang -f %{_sourcedir}/coreutils-lang.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 9.11-2
- Split lang payload into coreutils-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 9.11
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 9.11
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 9.3-1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 8.30-1
- Initial RPM
