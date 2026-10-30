Name:       sqlite
Version:    3.53.4
Release:    1
Summary:    SQLite database engine
License:    Public Domain
Source0:    sqlite-autoconf-3530400.tar.gz
Prefix:     /usr
Provides:   libsqlite3.so()(64bit)

%description
SQLite is a C library that implements an SQL database engine.

%prep
%setup -q -n sqlite-autoconf-3530400

%build
CPPFLAGS="-DSQLITE_ENABLE_COLUMN_METADATA=1 \
          -DSQLITE_ENABLE_UNLOCK_NOTIFY=1 \
          -DSQLITE_ENABLE_DBSTAT_VTAB=1 \
          -DSQLITE_SECURE_DELETE=1" \
%configure --disable-static --enable-fts{4,5}
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/bin/sqlite3
/usr/include/sqlite3*.h
/usr/lib64/libsqlite3.so*
/usr/lib64/pkgconfig/sqlite3.pc
/usr/share/man/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.53.4
- Renamed from sqlite3 and synced with LFS r13.1
