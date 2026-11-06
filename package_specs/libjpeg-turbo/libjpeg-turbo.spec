Name:       libjpeg-turbo
Version:    3.2.1
Release:    3
Summary:    JPEG library
License:    IJG AND BSD-3-Clause AND Zlib
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
%description
libjpeg-turbo is a fork of the original IJG libjpeg which uses SIMD to accelerate baseline JPEG compression and decompression.

%package doc
Summary:    libjpeg-turbo documentation
Requires:   libjpeg-turbo = %{version}-%{release}

%description doc
Documentation for libjpeg-turbo.

%prep
%setup -q

%build

mkdir build
pushd build

cmake -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_BUILD_TYPE=RELEASE  \
      -DENABLE_STATIC=FALSE       \
      -DCMAKE_INSTALL_DOCDIR=/usr/share/doc/libjpeg-turbo-%{version} \
      -DCMAKE_INSTALL_DEFAULT_LIBDIR=lib64  \
      -DCMAKE_SKIP_INSTALL_RPATH=ON \
      ..
%make_build
popd

%install    
rm -rf %{buildroot}
pushd build
%make_install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libjpeg-turbo.filelist
%files doc -f %{_sourcedir}/libjpeg-turbo-doc.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.2.1-3
- Record the verified license (IJG AND BSD-3-Clause AND Zlib): LICENSE.md (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.2.1-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.2.1-1
- Update to 3.2.1 (current upstream version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.2.0-2
- Split doc, devel payload into libjpeg-turbo-doc, libjpeg-turbo-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 3.2.0
- Sync with 3.0.0

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 3.0.0-1
- Version bump
