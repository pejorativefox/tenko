Name:       font-xfree86-type1
Version:    1.0.5
Release:    2
Summary:    XFree86 cursor Type1 font for X11
License:    X11
URL:        https://gitlab.freedesktop.org/xorg/font/xfree86-type1
Prefix:     /usr
Source0:    font-xfree86-type1-1.0.5.tar.xz



%description
This package contains the XFree86 cursor Type 1 font, cursor.pfa, for use
in the X Window System.

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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.5-2
- Replace the TODO summary/description and record the verified license
  (X11): COPYING (issue #8).

# let's skip this for now

