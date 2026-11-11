Name:       xrefresh
Version:    1.1.1
Release:    1
Summary:    Refresh the X11 screen
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xrefresh
Prefix:     /usr
Source0:    xrefresh-1.1.1.tar.xz
BuildRequires: libx11
BuildRequires: util-macros
BuildRequires: xorgproto



%description
Refresh the X11 screen.

xrefresh is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xrefresh.filelist
%changelog
# let's skip this for now

