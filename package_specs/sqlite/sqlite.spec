Name:       sqlite
Version:    3.53.4
Release:    3
Summary:    SQLite database engine
License:    Public Domain
Source0:    sqlite-autoconf-3530400.tar.gz
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
%setup -q -n sqlite-autoconf-3530400

%build
CPPFLAGS="-DSQLITE_ENABLE_COLUMN_METADATA=1 \
          -DSQLITE_ENABLE_UNLOCK_NOTIFY=1 \
          -DSQLITE_ENABLE_DBSTAT_VTAB=1 \
          -DSQLITE_SECURE_DELETE=1" \
./configure --prefix=/usr --libdir=%{_libdir} --disable-static \
    --enable-fts4 --enable-fts5
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/sqlite.filelist
%files devel -f %{_sourcedir}/sqlite-devel.filelist


%changelog
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
