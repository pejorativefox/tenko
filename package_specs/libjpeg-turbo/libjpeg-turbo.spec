Name:       libjpeg-turbo
Version:    3.2.1
Release:    1
Summary:    JPEG library
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
%description
libjpeg-turbo is a fork of the original IJG libjpeg which uses SIMD to accelerate baseline JPEG compression and decompression.

%package doc
Summary:    libjpeg-turbo documentation
Requires:   libjpeg-turbo = %{version}-%{release}

%description doc
Documentation for libjpeg-turbo.

%package devel
Summary:    libjpeg-turbo development files
Requires:   libjpeg-turbo = %{version}-%{release}

%description devel
Development files for libjpeg-turbo.

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
%files devel -f %{_sourcedir}/libjpeg-turbo-devel.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.2.1-1
- Update to 3.2.1 (current BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.2.0-2
- Split doc, devel payload into libjpeg-turbo-doc, libjpeg-turbo-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 3.2.0
- Sync with BLFS r13.1 (3.0.0)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 3.0.0-1
- Version bump
