Name:       libass
Version:    0.17.5
Release:    2
Summary:    Portable ASS/SSA subtitle renderer
License:    ISC
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
libass is a portable subtitle renderer for the ASS/SSA (Advanced
Substation Alpha/Substation Alpha) subtitle format. It is mostly
compatible with VSFilter.

%prep
%setup -q -a0

%build
%configure --prefix=/usr --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/include/ass/ass.h
/usr/include/ass/ass_types.h
/usr/lib64/libass.so
/usr/lib64/libass.so.9
/usr/lib64/libass.so.9.4.2
/usr/lib64/pkgconfig/libass.pc

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.17.5-2
- Replace the TODO summary/description and record the verified license
  (ISC): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.17.5-1
- Sync with the base set

# let's skip this for now
