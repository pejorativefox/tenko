Name:       libdrm
Version:    2.4.134
Release:    3
Summary:    Userspace interface to kernel DRM services
License:    MIT
URL:        https://gitlab.freedesktop.org/mesa/libdrm
Prefix:     /usr
Source0:    libdrm-2.4.134.tar.xz
BuildRequires: cairo
BuildRequires: libpciaccess
BuildRequires: xorgproto
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: harfbuzz
BuildRequires: libXdmcp
BuildRequires: liblzo2
BuildRequires: libpng
BuildRequires: libx11
BuildRequires: libxau
BuildRequires: libxcb
BuildRequires: libxext
BuildRequires: libxrender
BuildRequires: pixman
BuildRequires: python3-docutils

%description
libdrm provides a userspace library for the kernel Direct Rendering Manager.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release -Dudev=true -Dtests=false -Dvalgrind=disabled
ninja
popd

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libdrm.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.4.134-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.4.134-2
- Split devel payload into libdrm-devel (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.4.134-1
- Initial package
