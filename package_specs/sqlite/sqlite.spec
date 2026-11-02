Name:       sqlite
Version:    3.54.1
Release:    1
Summary:    SQLite database engine
License:    Public Domain
Source0:    sqlite-autoconf-3540100.tar.gz
Prefix:     /usr
Provides:   libsqlite3.so()(64bit)

%description
SQLite is a C library that implements an SQL database engine.

%package devel
Summary:    sqlite development files
Requires:   sqlite = %{version}-%{release}

%description devel
Development files for sqlite.

%prep
%setup -q -n sqlite-autoconf-3540100

%build
# Give the shared library a stable SONAME.  sqlite-autoconf links with
# -release (libsqlite3.so.<version>) and ships no SONAME, so consumers record
# the unversioned link name as their runtime requirement.  With this flag the
# library advertises libsqlite3.so.0 and new links record it.
CPPFLAGS="-DSQLITE_ENABLE_COLUMN_METADATA=1 \
          -DSQLITE_ENABLE_UNLOCK_NOTIFY=1 \
          -DSQLITE_ENABLE_DBSTAT_VTAB=1 \
          -DSQLITE_SECURE_DELETE=1" \
LDFLAGS="${LDFLAGS:-} -Wl,-soname,libsqlite3.so.0" \
./configure --prefix=/usr --libdir=%{_libdir} --disable-static \
    --enable-fts4 --enable-fts5
# LFS clears LDFLAGS.rpath: a standard-location install needs no runpath.
%make_build LDFLAGS.rpath=""

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/sqlite.filelist
%files devel -f %{_sourcedir}/sqlite-devel.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.54.1-1
- Update to 3.54.1 (autoconf 3540100), the current LFS trunk version.
- Add the missing SONAME: libsqlite3.so.<version> now carries
  libsqlite3.so.0, so consumers link against a versioned ABI instead of the
  unversioned file name.  The runtime package keeps the unversioned
  libsqlite3.so symlink and the explicit `Provides: libsqlite3.so()(64bit)`
  so already-built consumers keep working until they are rebuilt.
- Clear LDFLAGS.rpath as the book does; the library had a /usr/lib64
  RUNPATH baked in.
* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.53.4-3
- Keep /usr/lib64/libsqlite3.so in the runtime package.  This build has no
  SONAME (the library is libsqlite3.so.3.53.4), so every consumer, including
  rpm and Python's _sqlite3, records NEEDED libsqlite3.so.  The -devel split
  had moved it out and broke rpm on the installed system; -devel now ships
  only the headers and sqlite3.pc
* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.53.4-2
- Split devel payload into sqlite-devel (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.53.4
- Renamed from sqlite3 and synced with LFS r13.1
