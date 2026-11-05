Name:       rpm
Version:    4.18.1
Release:    8
Summary:    RPM package manager
License:    GPL-2.0-or-later AND LGPL-2.0-or-later
Source0:    %{name}-%{version}.tar.bz2
Patch0:     rpm-4.18.1-sqlite-global-log.patch
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
%patch 0 -p1

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
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.18.1-8
- Record the verified license (GPL-2.0-or-later AND LGPL-2.0-or-later): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.18.1-7
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 4.18.1-6
- Backport upstream d018e756b72c ("Don't muck with per-process global
  sqlite configuration from the db backend"): drop the process-global
  SQLITE_CONFIG_LOG handler that kept a stale rpmdb pointer.  Once the
  rpmdb had been closed, the next sqlite log message from any other
  connection in the process (libdnf's history.sqlite) reached rpmlog()
  with freed memory in rdb->db_descr and crashed inside vsnprintf.
  This is what made `dnf list installed`, `dnf info` and `dnf history`
  segfault.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.18.1-5
- Rebuild for Python 3.15 (3.14 site-packages are gone); 1 paths updated.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.18.1-4
- Wire up the python3-rpm subpackage: the spec declared it since 4.18.1-2
  but never added a %files section, so the bindings shipped inside rpm and
  the stale python3-rpm-4.18.1-2 required rpm = 4.18.1-2 (no provider).
  The five /usr/lib64/python3.15/site-packages/rpm* paths move to
  rpm-python.filelist; rpm.filelist no longer lists them.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.18.1-3
- Split devel payload into rpm-devel (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.18.1-2
- Enable the Python 3 bindings and split them into python3-rpm for the E1
  dnf/libdnf chain (dnf 4 imports the rpm module).  The main rpm package
  contents are unchanged.
- Keep --without-lua/--without-selinux/--without-cap/--without-acl and the
  existing libelf/sqlite/OpenSSL configuration.
