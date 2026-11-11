Name:       xwd
Version:    1.0.10
Release:    2
Summary:    X window image dump utility
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xwd
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz



%description
xwd is an X Window System window dumping utility. It allows X users to store
window images in a specially formatted dump file that can be read by other X
utilities for redisplay, printing, editing, formatting or image processing.

%prep
%setup -a 0

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xwd.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.10-2
- Replace the TODO summary/description and record the verified license
  (MIT): COPYING (issue #8).

# let's skip this for now

