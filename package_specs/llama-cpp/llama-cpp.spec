Name:       llama-cpp
Version:    1.0.0
Release:    1
Summary:    LLM inference engine with a Vulkan GPU backend
License:    MIT
URL:        https://github.com/ggml-org/llama.cpp
Prefix:     /usr
Source0:    llama.cpp-%{version}.tar.gz

BuildRequires: cmake
BuildRequires: ninja
BuildRequires: gcc
BuildRequires: pkgconf
BuildRequires: vulkan-headers
BuildRequires: vulkan-loader
BuildRequires: shaderc
BuildRequires: spirv-headers

%description
llama.cpp is an LLM inference engine for Meta's LLaMA models and other
GGUF models: llama-cli, llama-server (OpenAI-compatible HTTP API with a
built-in web UI), llama-quantize, llama-bench, llama-perplexity,
llama-imatrix and the rest of the tool suite, plus the libllama, libmtmd
and libggml shared libraries.

Built with the Vulkan backend (GGML_VULKAN=ON): the ggml-vulkan backend
runs model compute on any GPU with a Vulkan 1.3 ICD (RADV, ANV, NVIDIA),
with shaders compiled at build time by glslc and embedded into the
backend library.  The CPU fallback backend is compiled for the generic
x86-64 baseline (GGML_NATIVE=OFF), so the RPM is portable across hosts;
Vulkan carries the heavy compute.

%prep
%setup -q -n llama.cpp-%{version}

%build
cmake -S . -B build -G Ninja            \
      -DCMAKE_INSTALL_PREFIX=/usr       \
      -DCMAKE_BUILD_TYPE=Release        \
      -DCMAKE_INSTALL_LIBDIR=lib64      \
      -DGGML_VULKAN=ON                  \
      -DGGML_NATIVE=OFF                 \
      -DLLAMA_BUILD_NUMBER=12359        \
      -DLLAMA_BUILD_COMMIT=b1b770d
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install
install -Dpm0644 LICENSE %{buildroot}%{_datadir}/licenses/%{name}/LICENSE

%check
export LD_LIBRARY_PATH=%{buildroot}%{_libdir}
%{buildroot}%{_bindir}/llama-cli --version 2>&1 | tee version.txt
grep -q 'version:' version.txt
grep -q 'b1b770d' version.txt
test -e %{buildroot}%{_libdir}/libggml-vulkan.so

%files -f %{_sourcedir}/%{name}.filelist

%changelog
* Wed Nov 18 2026 tenko <build@tenko.invalid> 1.0.0-1
- New package, not in the base set: latest upstream stable release
  (1.0.0, checked 2026-11-18).  Built with the Vulkan GPU backend
  (GGML_VULKAN=ON); shaders are compiled by glslc from the shaderc
  package and embedded in libggml-vulkan.  The CPU backend uses the
  generic x86-64 baseline (GGML_NATIVE=OFF) so the RPM is portable.
