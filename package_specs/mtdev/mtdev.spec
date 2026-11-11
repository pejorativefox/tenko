Name:       mtdev
Version:    1.1.7
Release:    3
Summary:    Multitouch protocol translation library
License:    MIT
URL:        https://bitmath.se/org/code/mtdev/
Prefix:     /usr
Source0:    mtdev-1.1.7.tar.bz2

%description
mtdev converts kernel multitouch events to the MT protocol.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/mtdev.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.1.7-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.7-1
- Initial package
