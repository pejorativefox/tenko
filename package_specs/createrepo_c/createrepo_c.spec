Name:       createrepo_c
Version:    1.2.6
Release:    5
Summary:    Creates a common metadata repository
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
createrepo_c is a C implementation of createrepo.  It generates the
repodata (primary, filelists, other, and the repomd indexes) needed by dnf
to consume a local or remote RPM repository.

%prep
%setup -q

%build
mkdir build
pushd build
cmake -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_INSTALL_LIBDIR=lib64      \
      -DCMAKE_BUILD_TYPE=Release       \
      -DBUILD_DOC_C=OFF                \
      -DENABLE_DRPM=OFF                \
      -DENABLE_PYTHON=OFF              \
      -DENABLE_BASHCOMP=OFF            \
      -DENABLE_THREADED_XZ_ENCODER=ON  \
      -DWITH_ZCHUNK=ON                 \
      -DWITH_LIBMODULEMD=ON            \
      ..
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} cmake --install .
popd

%files -f %{_sourcedir}/createrepo_c.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.6-5
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND LGPL-2.1-or-later): COPYING, src/createrepo_c.c and src/koji.c (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.2.6-4
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.6-1
- New package for the E1 self-hosted repo assembly work (replaces the host
  createrepo_c).  createrepo_c is not in LFS/BLFS; this is the current
  upstream release.
- Built with zchunk and libmodulemd metadata support.  Delta RPM (drpm)
  support is disabled and the optional Python bindings are not built.
- Use a generated static filelist.
