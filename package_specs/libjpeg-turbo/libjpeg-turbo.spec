Name:       libjpeg-turbo
Version:    3.2.0
Release:    1
Summary:    JPEG library
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
%description
libjpeg-turbo is a fork of the original IJG libjpeg which uses SIMD to accelerate baseline JPEG compression and decompression.

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


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 3.2.0
- Sync with BLFS r13.1 (3.0.0)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 3.0.0-1
- Version bump
