Name:       xwud
Version:    1.0.8
Release:    1
Summary:    Display an X11 image dumped by xwd
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xwud
Prefix:     /usr
Source0:    xwud-1.0.8.tar.xz
BuildRequires: libx11
BuildRequires: util-macros
BuildRequires: xorgproto



%description
Display an X11 image dumped by xwd.

xwud is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xwud.filelist
%changelog
# let's skip this for now

