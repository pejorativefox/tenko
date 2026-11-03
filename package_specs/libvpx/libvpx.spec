Name:       libvpx
Version:    1.17.0
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

BuildRequires: nasm

%description
TODO

%prep
%setup -q

%build
sed -i 's/cp -p/cp/' build/make/Makefile &&

mkdir -pv libvpx-build
pushd libvpx-build

../configure --prefix=/usr    \
             --enable-shared  \
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
/usr/lib/libvpx.so
/usr/lib/libvpx.so.12
/usr/lib/libvpx.so.12.1
/usr/lib/libvpx.so.12.1.0
/usr/lib/pkgconfig/vpx.pc

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.17.0-1
- Sync with BLFS r13.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.8.0-1
- Version bump
