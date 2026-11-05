Name:       cdrkit
Version:    1.1.11
Release:    1
Summary:    cdrkit is a collection of computer programs for CD and DVD authoring
License:    GPL-2.0-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
Patch0:     cdrkit-1.1.11-gcc10.patch
Patch1:     cdrkit-1.1.11-gcc16.patch
AutoReq: no

%description
cdrkit is a collection of computer programs for CD and DVD authoring.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
mkdir build
pushd build
cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DPREFIX=/usr ..
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} %make_install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/cdrkit.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.11-1
- Rebuild 1.1.11: not in the r13.1 book; latest upstream stable
  2026-11-05 (https://deb.debian.org/debian/pool/main/c/cdrkit/).
- Keep the existing -fno-common fix for `outfile` and add the minimal
  modern-toolchain patch: cmake_minimum_required (CMake 4 refuses the
  tree without it) and explicit checksum.h/md5.h includes, because GCC
  14+ turns implicit function declarations into errors.
- Install from the CMake build directory instead of the source tree.
