Name:       coreutils
Version:    9.12
Release:    2
Summary:    GNU operating system tools
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.xz
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
patch -Np1 -i %{_sourcedir}/coreutils-9.12-i18n-1.patch
# The i18n patch touches tests/local.mk.  The tarball's Makefile.in was
# generated with automake 1.18; refreshing its timestamp avoids an
# unnecessary automake run (the patched file only feeds the test harness).
touch Makefile.in po/Makefile.in.in

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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 9.12-2
- Record the verified license (GPL-3.0-or-later): src/ls.c (issue #8).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 9.12-1
- Update to 9.12 (current LFS/BLFS r13.1 trunk version).

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
