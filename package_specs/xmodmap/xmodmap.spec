Name:       xmodmap
Version:    1.0.12
Release:    2
Summary:    X keymap and pointer button mapping utility
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xmodmap
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: libx11
BuildRequires: util-macros
BuildRequires: xorgproto



%description
The xmodmap program is used to edit and display the keyboard modifier map
and keymap table that client applications use to convert event keycodes into
keysyms.

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

%files -f %{_sourcedir}/xmodmap.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.12-2
- Replace the TODO summary/description and record the verified license
  (MIT): COPYING (issue #8).

# let's skip this for now

