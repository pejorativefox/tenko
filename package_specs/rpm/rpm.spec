Name:       rpm
Version:    4.18.1
Release:    1
Summary:    RPM package manager
License:    GPL3
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Programs to manage, build and install using the RPM package format.

%prep
%setup -q

%build
export ac_cv_header_elfutils_libdwelf_h=no
%configure --without-lua \
           --without-python \
           --without-selinux \
           --without-cap \
           --without-acl \
           --without-readline \
           --disable-plugins \
           --disable-nls \
           --enable-libelf=yes \
           --enable-sqlite=yes \
           --with-crypto=openssl
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
rmdir %{buildroot}/var/tmp 2>/dev/null || true
rmdir %{buildroot}/var 2>/dev/null || true

%files -f %{_sourcedir}/rpm.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.18.1
- Replace directory globs with a generated static filelist

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 4.18.1-1
- Version bump

* Wed May 20 2020 Chris Statzer <chris.statzer@qq.com> 4.14.2.1-2
- Updated build to use python3
