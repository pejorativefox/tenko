Name:       duktape
Version:    2.7.0
Release:    3
Summary:    Embeddable JavaScript engine
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
Duktape is an embeddable JavaScript engine with a compact footprint.

%package devel
Summary:    Development files for duktape
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in duktape; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

%prep
%setup -q

%build
sed -i 's/-Os/-O2/' Makefile.sharedlibrary
make -f Makefile.sharedlibrary INSTALL_PREFIX=/usr

%install
rm -rf %{buildroot}
make -f Makefile.sharedlibrary INSTALL_PREFIX=%{buildroot}/usr install

%files -f %{_sourcedir}/duktape.filelist
%files devel

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 2.7.0-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.7.0
- Initial package (BLFS r13.1)
