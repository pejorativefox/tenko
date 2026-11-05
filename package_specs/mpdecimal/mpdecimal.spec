Name:       mpdecimal
Version:    4.0.1
Release:    4
Summary:    Decimal floating point library
License:    BSD-2-Clause
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
libmpdec is a library for arbitrary precision correctly rounded decimal
floating point arithmetic.

%prep
%setup -q

%build
%configure --disable-static --docdir=%{_docdir}/%{name}-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/mpdecimal.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.0.1-4
- Replace the legacy short licence name with the verified SPDX expression
  (BSD-2-Clause): COPYRIGHT.txt, 2-clause BSD (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 4.0.1-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.0.1
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.0.1
- Initial package (LFS r13.1)
