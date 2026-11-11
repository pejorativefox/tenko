Name:       xev
Version:    1.2.7
Release:    1
Summary:    Print the content of X11 events
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xev
Prefix:     /usr
Source0:    xev-1.2.7.tar.xz
BuildRequires: libx11
BuildRequires: libxrandr
BuildRequires: util-macros
BuildRequires: xorgproto



%description
Print the content of X11 events.

xev is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xev.filelist
%changelog
# let's skip this for now

