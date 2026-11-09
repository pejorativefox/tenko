Name:       vulkan-headers
Version:    1.4.363.0
Release:    1
Summary:    Khronos Vulkan headers and registry files
License:    Apache-2.0 OR MIT
Prefix:     /usr
Source0:    Vulkan-Headers-vulkan-sdk-1.4.363.0.tar.gz

BuildRequires: cmake
BuildRequires: ninja
BuildRequires: gcc

%description
The Khronos Vulkan headers: the C and C++ Vulkan declarations, the
Vulkan-Hpp wrappers, the video codec headers, and the XML/JSON registry
that describes the API.  The Vulkan loader and the programs that compile
against the Vulkan API build against these headers.

Version 1.4.363.0 is the latest stable upstream tag
(vulkan-sdk-1.4.363.0), the same Vulkan SDK generation as SPIRV-Tools
2026.4.

%prep
%setup -q -n Vulkan-Headers-vulkan-sdk-1.4.363.0

%build
cmake -S . -B build -G Ninja            \
      -DCMAKE_INSTALL_PREFIX=/usr       \
      -DCMAKE_BUILD_TYPE=Release        \
      -DVULKAN_HEADERS_ENABLE_TESTS=OFF \
      -DVULKAN_HEADERS_ENABLE_INSTALL=ON
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install

%files -f %{_sourcedir}/vulkan-headers.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 1.4.363.0-1
- Initial package: Vulkan-Headers from the Vulkan SDK 1.4.363.0
  release, the latest stable upstream tag and the same SDK generation
  as SPIRV-Tools 2026.4.  The Vulkan loader builds against these headers.
