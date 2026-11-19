Name:       tinyxml2
Version:    11.0.0
Release:    1
Summary:    Small, simple and efficient C++ XML parser
License:    Zlib
URL:        https://github.com/leethomason/tinyxml2
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

# BuildRequires: none (toolchain only)

%description
TinyXML-2 is a small, simple and efficient C++ XML parser that can be
easily integrated into other programs.  It parses XML into a DOM tree
of XML nodes and prints XML back out, supports UTF-8 and legacy
encodings, and is dependency-free.  This build produces the shared
library, the header, and the pkg-config and CMake package files.

tinyxml2 is not part of the base set; it is packaged as the XML-RPC
parsing backend for rtorrent.

%prep
%setup -q

%build
cmake -S . -B build -G Ninja            \
      -DCMAKE_INSTALL_PREFIX=/usr       \
      -DCMAKE_BUILD_TYPE=Release        \
      -DCMAKE_INSTALL_LIBDIR=lib64      \
      -DBUILD_SHARED_LIBS=ON            \
      -Dtinyxml2_BUILD_TESTING=OFF
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install

%files -f %{_sourcedir}/tinyxml2.filelist

%changelog
* Fri Nov 20 2026 tenko <build@tenko.invalid> 11.0.0-1
- New package, not in the base set: latest upstream stable release
  (11.0.0, checked 2026-11-20).  Packaged as the XML-RPC parsing
  backend for rtorrent; installs the shared library, header,
  tinyxml2.pc and the CMake package files.
