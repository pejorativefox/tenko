Name:       mesa
Version:    26.2.3
Release:    1
Summary:    Mesa 3D Graphics Library
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

BuildRequires: libx11, libxext, libxfixes, libxrandr, libxxf86vm
BuildRequires: libxcb, libxshmfence, libdrm, llvm
Requires:   libxshmfence

%description
Open source implementations of OpenGL, OpenGL ES, EGL, GBM and the
llvmpipe software rasterizer, built for X11 only (no Wayland, no Vulkan).

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                \
      --prefix=/usr           \
      --buildtype=release     \
      -Dplatforms=x11         \
      -Dgallium-drivers=llvmpipe \
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
* Sun Nov 01 2026 browneye <build@browneye.invalid> 26.2.3-1
- Sync with BLFS r13.1: X11-only, llvmpipe, no Wayland/Vulkan.
