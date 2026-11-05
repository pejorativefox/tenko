Name:       nghttp2
Version:    1.70.0
Release:    3
Summary:    HTTP/2 C library and tools
License:    MIT
URL:        https://nghttp2.org/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
nghttp2 is an implementation of HTTP/2 and its header compression algorithm
HPACK.  This package builds the library only (BLFS --enable-lib-only), which
is what Node.js links against with --shared-nghttp2.

%prep
%setup -q -n %{name}-%{version}

%build
%configure --disable-static \
           --enable-lib-only \
           --docdir=/usr/share/doc/%{name}-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/nghttp2.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.70.0-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sun Nov 01 2026 Browneye Node.js wave <daspork@browneye.invalid> 1.70.0-1
- New package (BLFS r13.1 packages.ent nghttp2-version 1.70.0).
- Source: https://github.com/nghttp2/nghttp2/releases/download/v1.70.0/nghttp2-1.70.0.tar.xz
  md5 3df2b4b51caa13b76032bfd2d11d4ab2
  sha256 e05cb1388eaca3830aded4ccf20044b6e1ac1a61411dcca11b0437c4285c8bc2
- Configure: ./configure --prefix=/usr --disable-static --enable-lib-only
  --docdir=/usr/share/doc/nghttp2-1.70.0 (BLFS r13.1 command).
- Static filelist generated from the install tree.
