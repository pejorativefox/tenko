Name:       xwininfo
Version:    1.1.7
Release:    2
Summary:    X window information utility
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xwininfo
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: libxcb
BuildRequires: util-macros
BuildRequires: xorgproto
BuildRequires: libXdmcp
BuildRequires: libxau
BuildRequires: libx11



%description
xwininfo is a utility for displaying information about windows. The target
window can be selected with the mouse or specified by window id or name.

%prep
%setup -a 0

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xwininfo.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.7-2
- Replace the TODO summary/description and record the verified license
  (MIT): COPYING (issue #8).

# let's skip this for now

