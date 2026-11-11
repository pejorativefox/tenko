Name:       font-misc-ethiopic
Version:    1.0.5
Release:    2
Summary:    Goha-Tibeb Zemen Ethiopic fonts for X11
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/font/misc-ethiopic
Prefix:     /usr
Source0:    font-misc-ethiopic-1.0.5.tar.xz
BuildRequires: util-macros
BuildRequires: mkfontscale
BuildRequires: font-util



%description
This package contains the Goha-Tibeb Zemen fonts from the Ge'ez Frontiers
Foundation, providing Ethiopic (Ge'ez) script coverage for the X Window
System.

%prep
%setup -a 0

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/font-misc-ethiopic.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.5-2
- Replace the TODO summary/description and record the verified license
  (MIT): COPYING (issue #8).

# let's skip this for now

