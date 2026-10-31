Name:       libepoxy
Version:    1.5.10
Release:    1
Summary:    OpenGL function management
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

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
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.10-1
- Version bump
