Name:       lz4
Version:    1.10.0
Release:    1
Summary:    Extremely fast compression algorithm
License:    BSD
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
LZ4 is a lossless compression algorithm, providing compression speed at
400 MB/s per core, and a fast decoder.

%prep
%setup -q

%build
make -j%{_smp_build_ncpus} BUILD_STATIC=no PREFIX=/usr

%install
rm -rf %{buildroot}
make BUILD_STATIC=no PREFIX=/usr libdir=/usr/lib64 DESTDIR=%{buildroot} install

%files -f %{_sourcedir}/lz4.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.10.0
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.10.0
- Initial package (LFS r13.1)
