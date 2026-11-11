Name:       xcursor-themes
Version:    1.0.7
Release:    1
Summary:    Default X11 cursor themes
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/data/cursors
Prefix:     /usr
Source0:    xcursor-themes-1.0.7.tar.xz

BuildRequires: xcursorgen

%description
Default X11 cursor themes.

xcursor-themes is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xcursor-themes.filelist
%changelog
# let's skip this for now

