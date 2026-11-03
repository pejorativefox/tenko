Name:       libglu
Version:    9.0.3
Release:    1
Summary:    This package provides the Mesa OpenGL Utility library. 
License:    NO_IDEA
Source0:    glu-%{version}.tar.xz
Prefix:     /usr

%description
This package provides the Mesa OpenGL Utility library. 

%prep
%setup -n glu-%{version}

%build
mkdir build
pushd build
meson setup ..               \
      --prefix=/usr          \
      --buildtype=release    \
      -D gl_provider=gl      \
      --default-library=shared
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files
/usr/include/GL/glu.h
/usr/lib64/libGLU.so
/usr/lib64/libGLU.so.1
/usr/lib64/libGLU.so.1.3.1
/usr/lib64/pkgconfig/glu.pc

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 9.0.3-1
- Sync with BLFS r13.1

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 9.0.1-1
- Initial RPM

