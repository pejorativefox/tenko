Name:       font-ibm-type1
Version:    1.0.4
Release:    2
Summary:    IBM Type1 fonts for X11
License:    IBM/MIT X Consortium Courier Typefont agreement
Prefix:     /usr
Source0:    font-ibm-type1-1.0.4.tar.xz



%description
This package contains the IBM Courier Type 1 fonts for use in the X Window
System, distributed under the IBM/MIT X Consortium Courier Typefont
agreement.

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

%files -f %{_sourcedir}/font-ibm-type1.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.4-2
- Replace the TODO summary/description and record the verified license
  (IBM/MIT X Consortium Courier Typefont agreement, no SPDX identifier): COPYING (issue #8).

# let's skip this for now

