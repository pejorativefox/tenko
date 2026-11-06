Name:       libcap-ng
Version:    0.9.6
Release:    1
Summary:    An alternate POSIX capabilities library
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
URL:        https://github.com/stevegrubb/libcap-ng

BuildRequires: gcc
BuildRequires: make
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
BuildRequires: pkgconf

%description
Libcap-ng is a library that makes using POSIX capabilities easier.
The runtime package also contains the header, unversioned .so symlink,
pkg-config file and the pscap/netcap/filecap tools; there is no
-devel subpackage.

%prep
%setup -q

%build
./autogen.sh
%configure \
    --without-python \
    --disable-static \
    --disable-cap-audit
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -f %{buildroot}%{_libdir}/*.la
rm -f %{buildroot}%{_libdir}/*.a

%files -f %{_sourcedir}/libcap-ng.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.9.6-1
- Not in the base set: added as OpenVPN 2.7.8's hard
  dependency, at the latest upstream stable release (v0.9.6,
  2026-09-09).  The library is LGPL-2.1-or-later; the bundled
  pscap/netcap/filecap tools are GPL-2.0-or-later.
