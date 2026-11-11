Name:       xmessage
Version:    1.0.7
Release:    1
Summary:    Display X11 text messages or question dialogs
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xmessage
Prefix:     /usr
Source0:    xmessage-1.0.7.tar.xz
BuildRequires: libx11
BuildRequires: libxaw
BuildRequires: libxt
BuildRequires: util-macros



%description
Display X11 text messages or question dialogs.

xmessage is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xmessage.filelist
%changelog
# let's skip this for now

