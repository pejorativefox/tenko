Name:       libbsd
Version:    0.12.2
Release:    6
Summary:    BSD compatibility library
License:    BSD-3-Clause
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: libmd

%description
BSD compatibility library used by shadow (readpassphrase).

%prep
%setup -q

%build
%configure --disable-static --without-libbsd
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libbsd.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.12.2-6
- Replace the legacy short licence name with the verified SPDX expression
  (BSD-3-Clause): COPYING, whose Files: * stanza is BSD-3-clause (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.12.2-5
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.12.2-4
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.12.2-2
- Move the pkg-config files into a new -devel subpackage so the runtime
  package no longer drags pkgconfig(...) consumers into every install.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.12.2
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 0.12.2
- Bootstrap dependency for shadow
