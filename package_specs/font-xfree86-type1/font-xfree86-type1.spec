Name:       font-xfree86-type1
Version:    1.0.5
Release:    1
Summary:    CrossUnicode Type1 fonts for X11
License:    GPL3
Prefix:     /usr
Source0:    font-xfree86-type1-1.0.5.tar.xz



%description
TODO

%prep
%setup -a 0

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
rm -rf %{buildroot}/usr/share/fonts/X11/Type1/fonts.dir
rm -rf %{buildroot}/usr/share/fonts/X11/Type1/fonts.scale

%files -f %{_sourcedir}/font-xfree86-type1.filelist
%changelog
# let's skip this for now

