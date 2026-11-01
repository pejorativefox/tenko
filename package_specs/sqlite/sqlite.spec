Name:       sqlite
Version:    3.53.4
Release:    2
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
* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.53.4-2
- Split devel payload into sqlite-devel (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.53.4
- Renamed from sqlite3 and synced with LFS r13.1
