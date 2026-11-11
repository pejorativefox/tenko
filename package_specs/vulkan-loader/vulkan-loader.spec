Name:       vulkan-loader
Version:    1.4.363.0
Release:    1
Summary:    Khronos Vulkan loader library
License:    Apache-2.0
URL:        https://github.com/KhronosGroup/Vulkan-Loader
Prefix:     /usr
Source0:    Vulkan-Loader-vulkan-sdk-1.4.363.0.tar.gz

BuildRequires: cmake
BuildRequires: ninja
BuildRequires: gcc
BuildRequires: pkgconf
BuildRequires: vulkan-headers
BuildRequires: libx11, libxcb, libxrandr
BuildRequires: git

%description
The Khronos Vulkan loader, the libvulkan library that an application
links against.  The loader finds the installed ICD drivers and layers,
loads them, and dispatches the Vulkan entry points to them.

The package is built for X11: the Xlib, XCB and Xrandr window-system
interfaces are enabled; Wayland and DirectFB are not.  The development
payload (the unversioned .so link, vulkan.pc and the CMake package
files) ships in the runtime package, following the no -devel
subpackage rule.

Version 1.4.363.0 is the latest stable upstream tag
(vulkan-sdk-1.4.363.0).

%prep
%setup -q -n Vulkan-Loader-vulkan-sdk-1.4.363.0

%build
cmake -S . -B build -G Ninja            \
      -DCMAKE_INSTALL_PREFIX=/usr       \
      -DCMAKE_BUILD_TYPE=Release        \
      -DCMAKE_INSTALL_LIBDIR=lib64      \
      -DBUILD_WSI_WAYLAND_SUPPORT=OFF   \
      -DBUILD_WSI_DIRECTFB_SUPPORT=OFF  \
      -DBUILD_TESTS=OFF
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install

# The loader owns the system layer and ICD directories; driver packages
# install their ICD manifests into %{_datadir}/vulkan/icd.d.
mkdir -p %{buildroot}%{_sysconfdir}/vulkan/explicit_layer.d \
         %{buildroot}%{_sysconfdir}/vulkan/icd.d \
         %{buildroot}%{_sysconfdir}/vulkan/implicit_layer.d
mkdir -p %{buildroot}%{_datadir}/vulkan/explicit_layer.d \
         %{buildroot}%{_datadir}/vulkan/icd.d \
         %{buildroot}%{_datadir}/vulkan/implicit_layer.d

%files -f %{_sourcedir}/vulkan-loader.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 1.4.363.0-1
- Initial package: Vulkan-Loader from the Vulkan SDK 1.4.363.0 release,
  the latest stable upstream tag.  X11-only WSI to match the rest of
  the distro.  Without a system loader, SDL_GPU and other Vulkan
  consumers find no device on Tenko.
