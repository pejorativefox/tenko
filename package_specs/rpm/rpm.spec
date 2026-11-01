Name:       rpm
Version:    4.18.1
Release:    4
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

%package devel
Summary:    rpm development files
Requires:   rpm = %{version}-%{release}

%description devel
Development files for rpm.

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

# The Python bindings are their own subpackage: rpm.filelist must not list
# these paths or rpmbuild fails with "File listed twice".
%files -f %{_sourcedir}/rpm.filelist
%files -n python3-rpm -f %{_sourcedir}/rpm-python.filelist
%files devel -f %{_sourcedir}/rpm-devel.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.18.1-4
- Wire up the python3-rpm subpackage: the spec declared it since 4.18.1-2
  but never added a %files section, so the bindings shipped inside rpm and
  the stale python3-rpm-4.18.1-2 required rpm = 4.18.1-2 (no provider).
  The five /usr/lib64/python3.14/site-packages/rpm* paths move to
  rpm-python.filelist; rpm.filelist no longer lists them.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.18.1-3
- Split devel payload into rpm-devel (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.18.1-2
- Enable the Python 3 bindings and split them into python3-rpm for the E1
  dnf/libdnf chain (dnf 4 imports the rpm module).  The main rpm package
  contents are unchanged.
- Keep --without-lua/--without-selinux/--without-cap/--without-acl and the
  existing libelf/sqlite/OpenSSL configuration.
