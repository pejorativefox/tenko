Name:       font-bh-type1
Version:    1.0.4
Release:    2
Summary:    Bigelow & Holmes Type1 fonts for X11
License:    Luxi
URL:        https://gitlab.freedesktop.org/xorg/font/bh-type1
Prefix:     /usr
Source0:    font-bh-type1-1.0.4.tar.xz
BuildRequires: util-macros
BuildRequires: mkfontscale



%description
This package contains the Luxi Type 1 fonts from Bigelow & Holmes Inc.,
with font instruction code by URW++ GmbH, for use in the X Window System.

%prep
%setup

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
rm -rf %{buildroot}/usr/share/fonts/X11/Type1/fonts.dir
rm -rf %{buildroot}/usr/share/fonts/X11/Type1/fonts.scale

%files -f %{_sourcedir}/font-bh-type1.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.4-2
- Replace the TODO summary/description and record the verified license
  (Luxi, no SPDX identifier): COPYING (issue #8).

# let's skip this for now

