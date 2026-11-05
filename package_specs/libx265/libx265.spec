Name:       libx265
Version:    4.3
Release:    1
Summary:    H.265/HEVC video encoder library
License:    GPL-2.0-or-later
Source0:    x265_%{version}.tar.gz
Prefix:     /usr

BuildRequires: cmake, nasm

%description
x265 provides a library for encoding video streams into the
H.265/HEVC format.

%prep
%setup -q -n x265_%{version}

%build
mkdir build-x265
pushd build-x265
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D LIB_INSTALL_DIR=%{_lib}  \
      -D GIT_ARCHETYPE=1          \
      -W no-author                \
      ../source
%make_build
popd

%install
rm -rf %{buildroot}
pushd build-x265
%make_install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libx265.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.3-1
- Update to 4.3, the version in the BLFS r13.1 book
  (multimedia/libdriv/x265.xml).
- Follow the book's cmake invocation (GIT_ARCHETYPE=1, -W no-author).
- Set LIB_INSTALL_DIR=lib64: x265 hardcodes a "lib" default for its
  libraries, pkg-config file and CMake targets.
- nasm is available and used for assembly; no yasm dependency.
