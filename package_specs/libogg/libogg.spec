Name:       libogg
Version:    1.3.6
Release:    4
Summary:    Ogg bitstream container library
License:    BSD-3-Clause
Prefix:     /usr
Source0:    libogg-1.3.6.tar.xz

%description
libogg is a library for working with the Ogg bitstream format. Ogg
arranges compressed bitstreams so that seeking, time stamping and error
recovery are possible, and it can mix several concurrent media streams
into a single physical bitstream.

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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.3.6-4
- Replace the TODO summary/description and record the verified license
  (BSD-3-Clause): COPYING (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.3.6-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.3.3-1
- Version bump

