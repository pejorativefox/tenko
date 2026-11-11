Name:       woff2
Version:    1.0.2
Release:    1
Summary:    Font format library
License:    MIT
URL:        https://github.com/google/woff2
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The primary purpose of the WOFF2 format is to efficiently package fonts linked to Web documents by means of CSS

%prep
%setup -q
sed -i '/output.h/i #include <cstdint>' src/woff2_out.cc

%build
mkdir out
pushd out
cmake -D CMAKE_INSTALL_PREFIX=/usr         \
      -D CMAKE_INSTALL_LIBDIR=lib64        \
      -D CMAKE_BUILD_TYPE=Release          \
      -D CMAKE_POLICY_VERSION_MINIMUM=3.5  \
      -D CMAKE_SKIP_INSTALL_RPATH=ON ..
%make_build
popd

%install
rm -rf %{buildroot}
pushd out
%make_install
popd

%files -f %{_sourcedir}/woff2.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.2-1
- Rebuild 1.0.2 (version already matches the base set).
- Basis: tenko.lock (woff2 1.0.2).
- Add the documented gcc-15+ fix: include <cstdint> in src/woff2_out.cc.
- Build as documented: Release build, CMAKE_POLICY_VERSION_MINIMUM=3.5
  and CMAKE_SKIP_INSTALL_RPATH=ON.  CMAKE_INSTALL_LIBDIR=lib64 keeps the
  distro's library layout.
- Requires brotli (published 1.2.1).
- Static filelist generated from the install tree.
