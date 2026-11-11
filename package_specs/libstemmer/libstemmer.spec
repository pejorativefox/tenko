Name:       libstemmer
Version:    3.2.0
Release:    1
Summary:    Snowball stemming algorithms
License:    BSD-3-Clause
URL:        https://snowballstem.org/
Source0:    libstemmer_c-%{version}.tar.gz
Prefix:     /usr

%description
libstemmer provides the Snowball stemming algorithms as a C library
(libstemmer_c).  It is used by text search and indexing software to
reduce words to a common stem.

%prep
%setup -q -n libstemmer_c-%{version}

%build
make libstemmer.a %{?_smp_mflags} \
     CC="%{__cc}" \
     CFLAGS="%{optflags} -fPIC" \
     CPPFLAGS="-Iinclude"
%{__cc} %{optflags} -shared -Wl,-soname,libstemmer.so.0 \
    -o libstemmer.so.0.0.0 \
    src_c/*.o runtime/*.o libstemmer/*.o

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_libdir}
install -d %{buildroot}%{_includedir}
install -p -m 755 libstemmer.so.0.0.0 %{buildroot}%{_libdir}/
ln -s libstemmer.so.0.0.0 %{buildroot}%{_libdir}/libstemmer.so.0
ln -s libstemmer.so.0.0.0 %{buildroot}%{_libdir}/libstemmer.so
install -p -m 644 include/libstemmer.h %{buildroot}%{_includedir}/

%files -f %{_sourcedir}/libstemmer.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.2.0-1
- Update to 3.2.0: not in the base set; latest upstream stable
  2026-11-05 (https://snowballstem.org/download.html).
- Adapt to the 3.x libstemmer_c tarball: it extracts to
  libstemmer_c-3.2.0 and only ships a rule for libstemmer.a, so build
  its objects with -fPIC and link libstemmer.so.0.0.0 (soname
  libstemmer.so.0) from them.  The public API lives in
  libstemmer/libstemmer.c, which is built into the archive and must
  be linked explicitly (a plain -shared link of the archive would
  pull in nothing).
- Install include/libstemmer.h explicitly; the tarball no longer has
  a bare include/ directory of public headers.
