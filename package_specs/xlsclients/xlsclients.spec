Name:       xlsclients
Version:    1.1.6
Release:    1
Summary:    List the clients connected to an X server
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xlsclients
Prefix:     /usr
Source0:    xlsclients-1.1.6.tar.xz
BuildRequires: libxcb
BuildRequires: util-macros
BuildRequires: xorgproto
BuildRequires: libXdmcp
BuildRequires: libxau



%description
List the clients connected to an X server.

xlsclients is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xlsclients.filelist
%changelog
# let's skip this for now

