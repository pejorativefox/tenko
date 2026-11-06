Name:       shadow
Version:    4.20.3
Release:    4
Summary:    Shadow password format tools
License:    BSD-3-Clause AND BSD-2-Clause AND 0BSD AND Unlicense AND GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The shadow-utils package includes the necessary programs for converting UNIX password files to the shadow password format.

%package lang
Summary:    shadow translations
Requires:   shadow = %{version}-%{release}

%description lang
Translations for shadow.

%prep
%setup -q -a0

%build
sed -i 's/groups$(EXEEXT) //' src/Makefile.in
find man -name Makefile.in -exec sed -i 's/groups\.1 / /'   {} \;
find man -name Makefile.in -exec sed -i 's/getspnam\.3 / /' {} \;
find man -name Makefile.in -exec sed -i 's/passwd\.5 / /'   {} \;

sed -i -e 's@#ENCRYPT_METHOD DES@ENCRYPT_METHOD SHA512@' \
       -e 's@/var/spool/mail@/var/mail@' etc/login.defs

%configure --with-{b,yes}crypt \
            --with-group-name-max-length=32
%make_build 

%install
rm -rf %{buildroot}
%make_install
rm -f %{buildroot}/usr/lib64/libsubid.a
rm -vf %{buildroot}%{_infodir}/dir*
rm -rf %{buildroot}/etc/pam.d

%post
pwconv
grpconv

%files -f %{_sourcedir}/shadow.filelist
%files lang -f %{_sourcedir}/shadow-lang.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.3-4
- Record the verified license (BSD-3-Clause AND BSD-2-Clause AND 0BSD AND Unlicense AND GPL-2.0-or-later): COPYING (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 4.20.3-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Mon Nov  2 2026 browneye <build@browneye.invalid> 4.20.3-1
- Update to 4.20.3 (current upstream version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.2-2
- Split lang payload into shadow-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.2
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.20.2
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 4.13-1
- Version bump

* Thu May 14 2020 Chris Statzer <chris.statzer@qq.com> 4.6-3
- Added post command to create /etc/shadow

