Name:       xset
Version:    1.2.6
Release:    2
Summary:    X user preference utility
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz



%description
The xset program is used to set or query various user preference options of
the display. Options control the bell, key click, auto-repeat, mouse
acceleration, screen saver, DPMS and font path.

%prep
%setup -a 0

%build
%configure 
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xset.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.6-2
- Replace the TODO summary/description and record the verified license
  (MIT): COPYING (issue #8).

# let's skip this for now

