Name:       shadow
Version:    4.20.2
Release:    1
Summary:    Shadow password format tools
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The shadow-utils package includes the necessary programs for converting UNIX password files to the shadow password format.

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

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.2
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.20.2
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 4.13-1
- Version bump

* Thu May 14 2020 Chris Statzer <chris.statzer@qq.com> 4.6-3
- Added post command to create /etc/shadow

