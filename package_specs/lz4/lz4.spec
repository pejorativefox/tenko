Name:       lz4
Version:    1.10.0
Release:    3
Summary:    Extremely fast compression algorithm
License:    BSD
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
LZ4 is a lossless compression algorithm, providing compression speed at
400 MB/s per core, and a fast decoder.

%package devel
Summary:    Development files for lz4
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in lz4; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

%prep
%setup -q

%build
make -j%{_smp_build_ncpus} BUILD_STATIC=no PREFIX=/usr

%install
rm -rf %{buildroot}
make BUILD_STATIC=no PREFIX=/usr libdir=/usr/lib64 DESTDIR=%{buildroot} install

%files -f %{_sourcedir}/lz4.filelist
%files devel

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.10.0-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.10.0
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.10.0
- Initial package (LFS r13.1)
