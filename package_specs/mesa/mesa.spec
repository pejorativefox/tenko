Name:       mesa
Version:    26.2.3
Release:    5
Summary:    Mesa 3D Graphics Library
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

BuildRequires: libx11, libxext, libxfixes, libxrandr, libxxf86vm
BuildRequires: libxcb, libxshmfence, libdrm, llvm-devel
Requires:   libxshmfence

%description
Open source implementations of OpenGL, OpenGL ES, EGL, GBM, the
llvmpipe software rasterizer and the virgl guest driver for QEMU's
virtio-gpu 3D device, built for X11 only (no Wayland, no Vulkan).

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                \
      --prefix=/usr           \
      --buildtype=release     \
      -Dplatforms=x11         \
      -Dgallium-drivers=llvmpipe,virgl \
      -Dvulkan-drivers=       \
      -Dglx=dri               \
      -Dglvnd=disabled        \
      -Dgbm=enabled           \
      -Dopengl=true           \
      -Dgles1=enabled         \
      -Dgles2=enabled         \
      -Degl=enabled           \
      -Dllvm=enabled          \
      -Dgallium-va=disabled   \
      -Dvideo-codecs=         \
      -Dvalgrind=disabled     \
      -Dlibunwind=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/mesa.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 26.2.3-5
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 26.2.3-4
- Split mesa-devel (headers, pkgconfig files and unversioned .so
  symlinks).  mesa's pkgconfig() requires were pulling libdrm/x11/xcb/
  xext/xfixes/xxf86vm-devel into every X install unless mesa-devel was
  installed; the runtime package now carries only the versioned libraries,
  DRI/GBM drivers and drirc data

* Sun Nov 01 2026 browneye <build@browneye.invalid> 26.2.3-3
- Add the virgl gallium driver (-Dgallium-drivers=llvmpipe,virgl) so a
  guest booted with QEMU -device virtio-vga-gl can use host-gl accelerated
  GL instead of falling back to llvmpipe.  Upstream lists virgl as a supported
  gallium driver for virglrender-enabled QEMU virtual GPUs.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 26.2.3-2
- Build against llvm-devel after the Fedora-style LLVM split; the old
  monolithic llvm package no longer carries headers/CMake/llvm-config

* Sun Nov 01 2026 browneye <build@browneye.invalid> 26.2.3-1
- Sync with the base set: X11-only, llvmpipe, no Wayland/Vulkan.
