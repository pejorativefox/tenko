Name:       libseccomp
Version:    2.6.1
Release:    4
Summary:    Seccomp userspace library
License:    LGPL-2.1-only
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Userspace library for the Linux seccomp filter.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libseccomp.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.6.1-4
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-only): LICENSE, plus src/db.c "terms of version 2.1 of the GNU LGPL" (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 2.6.1-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.6.0
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.6.0
- Bootstrap dependency for man-db/systemd
