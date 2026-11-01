Name:       nodejs
Version:    26.13.0
Release:    1
Summary:    JavaScript runtime built on Chrome's V8 JavaScript engine
License:    MIT
URL:        https://nodejs.org/
Source0:    node-v%{version}.tar.xz
Patch0:     node-brotli-1.2.0-compat.patch
Prefix:     /usr

%description
Node.js is a JavaScript runtime built on Chrome's V8 JavaScript engine.  It
uses an event-driven, non-blocking I/O model and ships the npm package
manager.  This build links against the system brotli, c-ares, ICU, libuv,
nghttp2, OpenSSL, simdutf, and zlib instead of the bundled copies.

%prep
%setup -q -n node-v%{version}
%patch -P0 -p1

%build
./configure --prefix=/usr          \
            --shared-brotli        \
            --shared-cares         \
            --shared-libuv         \
            --shared-nghttp2       \
            --shared-openssl       \
            --shared-simdutf       \
            --shared-zlib          \
            --with-intl=system-icu
make %{_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
ln -sf node %{buildroot}/usr/share/doc/node-%{version}

%files -f %{_sourcedir}/nodejs.filelist

%changelog
* Sun Nov 01 2026 Browneye Node.js wave <daspork@browneye.invalid> 26.13.0-1
- New package.  BLFS r13.1 pins Node.js 26.9.0; the user explicitly
  approved shipping 26.13.0 (same major, current upstream LTS) as an
  AGENTS.md version-parity exception.  See the Node.js wave report.
- Source: https://nodejs.org/dist/v26.13.0/node-v26.13.0.tar.xz
  md5 71f973f3444ea276f00b2eee37a70f58
  sha256 263f639ecfa7a17b49438d76cdbf9aff73179e3c7cb789da69b900718427fa2e
- Configure (BLFS r13.1 shared-library flags):
  ./configure --prefix=/usr --shared-brotli --shared-cares --shared-libuv
  --shared-nghttp2 --shared-openssl --shared-simdutf --shared-zlib
  --with-intl=system-icu
- Requires brotli 1.2.0, c-ares 1.34.8, icu4c 78.3, libuv 1.53.0,
  nghttp2 1.70.0, simdutf 9.2.1, openssl 4.0.2, and zlib 1.3.2 at runtime.
  simdutf is the system copy; the bundled deps/v8/third_party copy is not
  used because of --shared-simdutf.
- Static filelist generated from the install tree.
- Patch node-brotli-1.2.0-compat.patch: Node 26.13.0's tree references
  BROTLI_DECODER_ERROR_FORMAT_BLOCK_SWITCH, which exists in its bundled
  deps/brotli snapshot but not in the released brotli 1.2.0 headers
  (BLFS r13.1 version).  Guard the constant with #ifdef so --shared-brotli
  links against the system 1.2.0 copy; the JS constant is simply not
  exported when the system brotli lacks it.
