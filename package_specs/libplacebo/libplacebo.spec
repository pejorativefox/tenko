Name:       libplacebo
Version:    7.387.0
Release:    1
Summary:    GPU-accelerated image and video rendering library
License:    LGPL-2.1-or-later
URL:        https://github.com/haasn/libplacebo
Source0:    %{name}-%{version}.tar.gz
Source1:    glad2-2.0.8.tar.gz
Source2:    Vulkan-Headers-vulkan-sdk-1.4.363.0.tar.gz
Prefix:     /usr

BuildRequires: meson
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: mesa

%description
libplacebo is a library for processing image and video primitives and
shaders.  It provides a high-quality rendering pipeline for OpenGL and
Vulkan and is the rendering core used by mpv's GPU video output.

This build enables the OpenGL renderer and uses the glad loader that
libplacebo declares as a git submodule; the source archive does not carry
submodules, so the glad Python generator is supplied as Source1.  Vulkan
headers are supplied as Source2 because libplacebo compiles Vulkan stub code
even when the Vulkan renderer is disabled.  The Vulkan renderer and its
shader compilers are not built because Tenko does not ship a Vulkan loader.

%prep
%setup -q
mkdir -p 3rdparty/glad 3rdparty/Vulkan-Headers
tar -xf %{SOURCE1} -C 3rdparty/glad --strip-components=1
tar -xf %{SOURCE2} -C 3rdparty/Vulkan-Headers --strip-components=1

%build
mkdir build
pushd build
meson setup ..                            \
    --prefix=/usr                         \
    --libdir=/usr/lib64                   \
    --buildtype=release                   \
    -Ddemos=false                         \
    -Dtests=false                         \
    -Dvulkan=disabled                     \
    -Dglslang=disabled                    \
    -Dshaderc=disabled                    \
    -Dd3d11=disabled                      \
    -Dlcms=disabled                       \
    -Ddovi=disabled                       \
    -Dlibdovi=disabled                    \
    -Dunwind=disabled                     \
    -Dxxhash=disabled
ninja
popd

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install

%files -f %{_sourcedir}/libplacebo.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 7.387.0-1
- New package: libplacebo 7.387.0, latest stable upstream, required by
  mpv 0.42 for its GPU video output.  OpenGL only: Vulkan, glslang and
  shaderc are disabled because Tenko has no Vulkan loader.
