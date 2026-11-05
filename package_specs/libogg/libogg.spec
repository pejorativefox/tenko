Name:       libogg
Version:    1.3.6
Release:    3
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    libogg-1.3.6.tar.xz

%description
TODO

%prep
%setup -q

%build
%configure  --prefix=/usr    \
            --disable-static \
            --docdir=/usr/share/doc/libogg-1.3.3
%make_build

%install    
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libogg.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.3.6-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.3.3-1
- Version bump

