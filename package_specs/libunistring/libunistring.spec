Name:       libunistring
Version:    1.5
Release:    3
Summary:    GNU Unicode string library
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
libunistring provides functions for manipulating Unicode strings and for
manipulating C strings according to the Unicode standard.  It is a build
dependency of libidn2 (and through it libpsl and curl/rsync IDN support).

%package devel
Summary:    Development files for libunistring
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in libunistring; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

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
%files devel


%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.5-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.5-1
- New package (D8): current BLFS trunk version, needed by libidn2.
