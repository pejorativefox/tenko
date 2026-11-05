Name:       libvpx
Version:    1.17.0
Release:    2
Summary:    VP8/VP9 video codec library
License:    BSD-3-Clause
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

BuildRequires: nasm

%description
libvpx is the WebM project's VP8/VP9 codec SDK. It provides the vpxenc and
vpxdec tools and a library for encoding and decoding VP8 and VP9 video.

%prep
%setup -q

%build
sed -i 's/cp -p/cp/' build/make/Makefile &&

mkdir -pv libvpx-build
pushd libvpx-build

../configure --prefix=/usr            \
             --libdir=/usr/lib64       \
             --enable-shared           \
             --disable-static
%make_build
popd

%install    
rm -rf %{buildroot}
pushd libvpx-build
%make_install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/vpxdec
/usr/bin/vpxenc
/usr/include/vpx/vp8.h
/usr/include/vpx/vp8cx.h
/usr/include/vpx/vp8dx.h
/usr/include/vpx/vpx_codec.h
/usr/include/vpx/vpx_decoder.h
/usr/include/vpx/vpx_encoder.h
/usr/include/vpx/vpx_ext_ratectrl.h
/usr/include/vpx/vpx_frame_buffer.h
/usr/include/vpx/vpx_image.h
/usr/include/vpx/vpx_integer.h
/usr/include/vpx/vpx_tpl.h
/usr/lib64/libvpx.so
/usr/lib64/libvpx.so.12
/usr/lib64/libvpx.so.12.1
/usr/lib64/libvpx.so.12.1.0
/usr/lib64/pkgconfig/vpx.pc

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.17.0-2
- Replace the TODO summary/description and record the verified license
  (BSD-3-Clause): LICENSE (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.17.0-1
- Sync with BLFS r13.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.8.0-1
- Version bump
