Name:       libepoxy
Version:    1.5.10
Release:    3
Summary:    OpenGL function management
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: mesa-devel


%description
libepoxy is a library for handling OpenGL function pointer management. 

%package devel
Summary:    libepoxy development files
Requires:   libepoxy = %{version}-%{release}
Provides: pkgconfig(epoxy)

%description devel
Development files for libepoxy.

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
%files devel -f %{_sourcedir}/libepoxy-devel.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.5.10-3
- Declare BuildRequires: mesa-devel.  libepoxy's meson needs the GL/EGL
  headers to enable its GLX/EGL entry points; without the declaration the
  build silently used whatever headers happened to be in the image.
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.5.10-2
- Split devel payload into libepoxy-devel (size audit)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.10-1
- Version bump
