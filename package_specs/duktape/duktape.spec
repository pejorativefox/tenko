Name:       duktape
Version:    2.7.0
Release:    4
Summary:    Embeddable JavaScript engine
License:    MIT
URL:        https://duktape.org/
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
Duktape is an embeddable JavaScript engine with a compact footprint.

%prep
%setup -q

%build
sed -i 's/-Os/-O2/' Makefile.sharedlibrary
make -f Makefile.sharedlibrary INSTALL_PREFIX=/usr LIBDIR=/lib64

%install
rm -rf %{buildroot}
make -f Makefile.sharedlibrary INSTALL_PREFIX=%{buildroot}/usr LIBDIR=/lib64 install

%files -f %{_sourcedir}/duktape.filelist

%changelog
* Thu Nov 12 2026 tenko <build@tenko.invalid> 2.7.0-4
- Install the shared libraries and duktape.pc in /usr/lib64.  The
  Makefile defaults LIBDIR to /lib, so the package put libduktape in
  /usr/lib.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 2.7.0-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.7.0
- Initial package
