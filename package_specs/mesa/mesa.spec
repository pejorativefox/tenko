Name:       mesa
Version:    26.2.3
Release:    3
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
* Sun Nov 01 2026 browneye <build@browneye.invalid> 26.2.3-3
- Add the virgl gallium driver (-Dgallium-drivers=llvmpipe,virgl) so a
  guest booted with QEMU -device virtio-vga-gl can use host-gl accelerated
  GL instead of falling back to llvmpipe.  BLFS lists virgl as a supported
  gallium driver for virglrender-enabled QEMU virtual GPUs.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 26.2.3-2
- Build against llvm-devel after the Fedora-style LLVM split; the old
  monolithic llvm package no longer carries headers/CMake/llvm-config

* Sun Nov 01 2026 browneye <build@browneye.invalid> 26.2.3-1
- Sync with BLFS r13.1: X11-only, llvmpipe, no Wayland/Vulkan.
