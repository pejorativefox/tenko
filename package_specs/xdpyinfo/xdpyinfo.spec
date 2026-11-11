Name:       xdpyinfo
Version:    1.4.0
Release:    1
Summary:    Display information about an X server
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xdpyinfo
Prefix:     /usr
Source0:    xdpyinfo-1.4.0.tar.xz
BuildRequires: libx11
BuildRequires: libxcb
BuildRequires: libxext
BuildRequires: libxi
BuildRequires: libxinerama
BuildRequires: libxrender
BuildRequires: libxtst
BuildRequires: util-macros
BuildRequires: xorgproto



%description
Display information about an X server.

xdpyinfo is maintained at its pinned version and is built
with the standard autotools build inline in its spec.


%prep
%setup -q

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xdpyinfo.filelist
%changelog
# let's skip this for now

