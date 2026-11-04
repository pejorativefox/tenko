Name:       zchunk
Version:    1.5.5
Release:    4
Summary:    A file format designed for highly efficient deltas while maintaining good compression
License:    BSD
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
zchunk is a compressed file format that splits the file into independent
chunks, allowing a client to fetch only changed chunks when a file is
updated.

%package devel
Summary:    Development files for zchunk
Requires:   %{name} = %{version}-%{release}

%description devel
pkg-config files for zchunk, used to build software against it.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                 \
      --prefix=/usr            \
      --buildtype=release      \
      -Dwith-zstd=enabled      \
      -Dwith-openssl=enabled   \
      -Dwith-curl=disabled     \
      -Ddocs=false             \
      -Dtests=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/zchunk.filelist
%files devel -f %{_sourcedir}/zchunk-devel.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.5.5-4
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.5.5-2
- Move the pkg-config files into a new -devel subpackage so the runtime
  package no longer drags pkgconfig(...) consumers into every install.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.5.5-1
- Update to upstream 1.5.5 (was 1.1.4) for the E1 dnf/libdnf chain.
  zchunk is not documented in LFS/BLFS; this follows the version required
  by current librepo/createrepo_c (>= 0.9.11).
- Built with zstd and OpenSSL; the optional libcurl download backend is
  disabled (librepo does its own downloads).
- Use a generated static filelist.
