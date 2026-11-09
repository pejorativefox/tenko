Name:       mesa
Version:    26.2.3
Release:    7
Summary:    Mesa 3D Graphics Library
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

# The iris and crocus drivers make Mesa build its Intel CLC (mesa_clc), which
# needs LLVMSPIRVLib, SPIRV-Tools, clang-cpp and clang's opencl-c.h at build
# time, plus Mako and PyYAML for Mesa's generated tables.  These are build-only
# dependencies and are not runtime requirements of this package.
BuildRequires: libx11, libxext, libxfixes, libxrandr, libxxf86vm
BuildRequires: libxcb, libxshmfence, libdrm, llvm-devel
BuildRequires: spirv-llvm-translator, spirv-tools
BuildRequires: clang-libs, clang-resource-filesystem, clang-devel
BuildRequires: python-mako, python-pyyaml
Requires:   libxshmfence
Requires:   vulkan-loader

%description
Open source implementations of OpenGL, OpenGL ES, EGL, GBM and Vulkan,
built for X11 only (no Wayland).  Includes the llvmpipe software
rasterizer, the virgl guest driver for QEMU's virtio-gpu 3D device, the
hardware Gallium drivers crocus and iris (Intel) and radeonsi and r600
(AMD), and the Vulkan ICDs: RADV (AMD GCN1+), ANV (Intel Gen8+), Hasvk
(Intel Gen4-7.5) and lavapipe (software).

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                \
      --prefix=/usr           \
      --buildtype=release     \
      -Dplatforms=x11         \
      -Dgallium-drivers=llvmpipe,virgl,crocus,iris,radeonsi,r600 \
      -Dvulkan-drivers=amd,intel,intel_hasvk,swrast \
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
* Mon Nov 09 2026 browneye <build@browneye.invalid> 26.2.3-7
- Build the Vulkan drivers: RADV (amd), ANV (intel), Hasvk (intel_hasvk)
  and lavapipe (swrast).  The package shipped no Vulkan ICD, so SDL_GPU
  and other Vulkan consumers found no device on Tenko.
- Require vulkan-loader: the installed ICD manifests are only usable
  through the Khronos loader.

* Sun Nov 08 2026 browneye <build@browneye.invalid> 26.2.3-6
- Build the hardware Gallium drivers: crocus (Intel Gen4-7.5, e.g.
  Haswell), iris (Intel Gen8+), radeonsi (AMD GCN1+) and r600 (AMD
  R600-Evergreen).  The package previously shipped only llvmpipe and
  virgl, so systems with a supported GPU fell back to software
  rasterization and Chrome/ANGLE reported no hardware GL adapter.
  Keep llvmpipe and virgl for software and VM guests.
- Declare the CLC build chain in BuildRequires now that it is packaged:
  spirv-llvm-translator, spirv-tools, clang-libs,
  clang-resource-filesystem, python-mako and python-pyyaml (issue #51).
  A clean rebuild keeps the same file list, installed size and runtime
  dependencies.

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
