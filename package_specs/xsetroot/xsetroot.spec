Name:       xsetroot
Version:    1.1.4
Release:    1
Summary:    Set the X11 root window background and cursor
License:    MIT
Prefix:     /usr
Source0:    xsetroot-1.1.4.tar.xz

BuildRequires: xbitmaps

%description
Set the X11 root window background and cursor.

xsetroot is maintained at its BLFS r13.1 version and is built
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

%files -f %{_sourcedir}/xsetroot.filelist
%changelog
# let's skip this for now

