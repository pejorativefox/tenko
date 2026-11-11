Name:       xdriinfo
Version:    1.0.8
Release:    1
Summary:    Query DRI drivers on an X server
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xdriinfo
Prefix:     /usr
Source0:    xdriinfo-1.0.8.tar.xz
BuildRequires: libx11
BuildRequires: mesa
BuildRequires: util-macros
BuildRequires: xorgproto



%description
Query DRI drivers on an X server.

xdriinfo is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xdriinfo.filelist
%changelog
# let's skip this for now

