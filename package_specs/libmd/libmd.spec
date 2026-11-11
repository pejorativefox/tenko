Name:       libmd
Version:    1.3.0
Release:    4
Summary:    Message digest library
License:    BSD-3-Clause
URL:        https://www.hadrons.org/software/libmd/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Message digest library used by libbsd.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libmd.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.3.0-4
- Replace the legacy short licence name with the verified SPDX expression
  (BSD-3-Clause): COPYING, whose Files: * stanza is BSD-3-clause (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.3.0-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.3.0
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.3.0
- Bootstrap dependency for shadow/libbsd
