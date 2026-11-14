Name:       simde
Version:    0.8.2
Release:    1
Summary:    SIMD Everywhere: portable implementations of SIMD intrinsics
License:    MIT
URL:        https://github.com/simd-everywhere/simde
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch

BuildRequires: meson
BuildRequires: ninja

%description
SIMDe provides fast, portable implementations of SIMD intrinsics (SSE,
AVX, NEON, ...) as a header-only C/C++ library, so code written for one
instruction set builds on any platform.  kitty includes it for its
vectorised string handling.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release -Dtests=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
# Header-only: the .pc file is architecture independent.
mkdir -p %{buildroot}%{_datadir}/pkgconfig
mv %{buildroot}%{_libdir}/pkgconfig/simde.pc %{buildroot}%{_datadir}/pkgconfig/

%files -f %{_sourcedir}/simde.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 0.8.2-1
- New package, not in the base set: latest upstream stable release (0.8.2,
  checked 2026-11-14).  Header-only; needed to build kitty.
