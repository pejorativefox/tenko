Name:       libpsl
Version:    0.23.3
Release:    5
Summary:    Public Suffix List library
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
libpsl provides access to the Public Suffix List (a set of domain names
beyond the standard suffixes such as .com).  curl uses it to enforce
cookie and HSTS scoping correctly.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release
ninja %{?_smp_mflags}
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libpsl.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.23.3-5
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.23.3-4
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.23.3-2
- Move the pkg-config files into a new -devel subpackage so the runtime
  package no longer drags pkgconfig(...) consumers into every install.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.23.3-1
- New package (D8): current BLFS trunk version, built with libidn2; curl is
  rebuilt with PSL support instead of --without-libpsl.
