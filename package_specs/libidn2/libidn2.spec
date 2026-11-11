Name:       libidn2
Version:    2.3.8
Release:    4
Summary:    Internationalized domain name library
License:    GPL-3.0-or-later AND (GPL-2.0-or-later OR LGPL-3.0-or-later)
URL:        https://www.gnu.org/software/libidn/
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
libidn2 implements the IDNA2008, TR46 and IDNA2003 standards for
internationalized domain names (punycode conversion, validation and
lookup).  curl and rsync use it for IDN support.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libidn2.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.3.8-4
- Record the verified license (GPL-3.0-or-later AND (GPL-2.0-or-later OR LGPL-3.0-or-later)): README (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 2.3.8-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.3.8-1
- New package (D8): current trunk version, enables IDN in rsync and
  PSL support in libpsl/curl.
