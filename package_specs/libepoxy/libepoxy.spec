Name:       libepoxy
Version:    1.5.10
Release:    6
Summary:    OpenGL function management
License:    MIT
URL:        https://github.com/anholt/libepoxy
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: mesa

Provides: pkgconfig(epoxy)
%description
libepoxy is a library for handling OpenGL function pointer management. 

%prep
%setup -q

%build
mkdir -pv build
pushd build
meson setup .. --prefix=/usr -Dtests=false
ninja
popd

%install    
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libepoxy.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.5.10-6
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.5.10-5
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).
- Rebuild with the .pc Requires exclusion so epoxy.pc does not pull
  mesa into a runtime install.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.5.10-3
- Declare BuildRequires: mesa-devel.  libepoxy's meson needs the GL/EGL
  headers to enable its GLX/EGL entry points; without the declaration the
  build silently used whatever headers happened to be in the image.
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.5.10-2
- Split devel payload into libepoxy-devel (size audit)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.10-1
- Version bump
