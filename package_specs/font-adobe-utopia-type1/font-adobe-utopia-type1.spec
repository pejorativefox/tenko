Name:       font-adobe-utopia-type1
Version:    1.0.5
Release:    2
Summary:    Adobe Utopia Type1 fonts for X11
License:    Adobe-Utopia
URL:        https://gitlab.freedesktop.org/xorg/font/adobe-utopia-type1
Prefix:     /usr
Source0:    font-adobe-utopia-type1-1.0.5.tar.xz
BuildRequires: util-macros
BuildRequires: mkfontscale
BuildRequires: font-util
BuildRequires: fontconfig



%description
Adobe donated the Utopia typeface family to the X Consortium for use in the
X Window System. This package contains the Utopia Regular, Italic, Bold and
Bold Italic Type 1 fonts and their Adobe Font Metric files.

%prep
%setup -a 0

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/font-adobe-utopia-type1.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.5-2
- Replace the TODO summary/description and record the verified license
  (Adobe-Utopia): COPYING (issue #8).

# let's skip this for now

