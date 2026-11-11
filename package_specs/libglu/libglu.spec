Name:       libglu
Version:    9.0.3
Release:    2
Summary:    This package provides the Mesa OpenGL Utility library. 
License:    SGI-B-1.1 AND SGI-B-2.0 AND MIT
URL:        https://gitlab.freedesktop.org/mesa/glu
Source0:    glu-%{version}.tar.xz
Prefix:     /usr
BuildRequires: mesa
BuildRequires: libxfixes
BuildRequires: xorgproto
BuildRequires: libXdmcp
BuildRequires: libdrm
BuildRequires: libpciaccess
BuildRequires: libx11
BuildRequires: libxau
BuildRequires: libxcb
BuildRequires: libxext
BuildRequires: libxxf86vm

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

%files -f %{_sourcedir}/libglu.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 9.0.3-2
- Replace NO_IDEA with the verified license (SGI-B-1.1 AND SGI-B-2.0 AND MIT): meson.build license: field (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 9.0.3-1
- Sync with the base set

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 9.0.1-1
- Initial RPM

