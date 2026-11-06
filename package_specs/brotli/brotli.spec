Name:       brotli
Version:    1.2.1
Release:    3
Summary:    Brotli compression format
License:    MIT
URL:        https://github.com/google/brotli
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Brotli is a generic-purpose lossless compression algorithm that compresses
data using a combination of a modern variant of the LZ77 algorithm, Huffman
coding and second order context modeling.  This package provides the
libbrotli libraries and the brotli command.

%prep
%setup -q -n %{name}-%{version}

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D CMAKE_BUILD_TYPE=Release  \
      -G Ninja .. 
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/brotli.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.2.1-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Mon Nov  2 2026 browneye <build@browneye.invalid> 1.2.1-1
- Update to 1.2.1 (current upstream version).

* Sun Nov 01 2026 Browneye Node.js wave <daspork@browneye.invalid> 1.2.0-1
- Update 1.0.9 -> 1.2.0 (tenko.lock brotli-version).
- Source: https://github.com/google/brotli/archive/v1.2.0/brotli-1.2.0.tar.gz
  md5 8fbfae9a5ecbc278ae7f761ecb6d1285
  sha256 816c96e8e8f193b40151dad7e8ff37b1221d019dbcb9c35cd3fadbfe6477dfec
- Configure: cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib64
  -DCMAKE_BUILD_TYPE=Release -G Ninja (the documented build command plus the
  distro's /usr/lib64 layout; the cmake 4.4.3 RPM patches GNUInstallDirs
  to default to lib, so lib64 is set explicitly).
- Static filelist generated from the install tree.
