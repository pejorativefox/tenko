Name:       db
Version:    6.2.32
Release:    1
Summary:    Berkeley DB embedded database library
License:    AGPL-3.0-only
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Berkeley DB is an embedded database library providing transactions,
replication and a B-tree access method.

%prep
%setup -q -a0

%build
pushd build_unix
CFLAGS="-std=gnu17" CXXFLAGS="-std=gnu++17" \
../dist/configure --prefix=/usr      \
                  --enable-compat185 \
                  --enable-dbm       \
                  --disable-static   \
                  --enable-cxx
%make_build
popd

%install    
rm -rf %{buildroot}
pushd build_unix
%make_install docdir=/usr/share/doc/db-6.2.32
popd
rm -vf %{buildroot}%{_infodir}/dir*
rm -rf %{buildroot}/usr/share/doc/
%files -f %{_sourcedir}/db.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 6.2.32-1
- Rebuild 6.2.32 against the base toolchain.
- Basis: only the archived 5.3.28 entry is available;
  6.2.32 is the current upstream stable release and is already
  above the pinned version, so the version is unchanged.
- Source: https://download.oracle.com/berkeley-db/db-6.2.32.tar.gz
  md5 33491b4756cb44b91c3318b727e71023
- Built from build_unix as before.  GCC 16 defaults to C23, where an
  empty parameter list means (void), which breaks db's old-style
  function definitions ("incompatible pointer type" errors in
  env_config.c).  Build with CFLAGS=-std=gnu17 and
  CXXFLAGS=-std=gnu++17; no source patch is needed.
- Removed the stale empty "skip this" changelog stub.
- Static filelist generated from the install tree.
