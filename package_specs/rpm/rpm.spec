Name:       rpm
Version:    4.18.1
Release:    2
Summary:    RPM package manager
License:    GPL3
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Programs to manage, build and install using the RPM package format.

%package -n python3-rpm
Summary:    Python bindings for the RPM package manager
Requires:   %{name} = %{version}-%{release}

%description -n python3-rpm
The rpm Python module allows Python programs (notably dnf) to query the
RPM database and run transactions through librpm.

%prep
%setup -q

%build
export ac_cv_header_elfutils_libdwelf_h=no
%configure --without-lua \
           --enable-python \
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

%files -n python3-rpm -f %{_sourcedir}/rpm-python.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.18.1-2
- Enable the Python 3 bindings and split them into python3-rpm for the E1
  dnf/libdnf chain (dnf 4 imports the rpm module).  The main rpm package
  contents are unchanged.
- Keep --without-lua/--without-selinux/--without-cap/--without-acl and the
  existing libelf/sqlite/OpenSSL configuration.
