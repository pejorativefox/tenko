Name:       libunistring
Version:    1.5
Release:    4
Summary:    GNU Unicode string library
License:    LGPL-3.0-or-later OR GPL-2.0-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
libunistring provides functions for manipulating Unicode strings and for
manipulating C strings according to the Unicode standard.  It is a build
dependency of libidn2 (and through it libpsl and curl/rsync IDN support).

%prep
%setup -q

%build
%configure --disable-static --docdir=/usr/share/doc/libunistring-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libunistring.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.5-4
- Record the verified license (LGPL-3.0-or-later OR GPL-2.0-or-later): README (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.5-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.5-1
- New package (D8): current BLFS trunk version, needed by libidn2.
