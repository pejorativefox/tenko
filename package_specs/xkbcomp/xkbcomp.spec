Name:       xkbcomp
Version:    1.5.0
Release:    4
Summary:    XKB keyboard description compiler
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xkbcomp
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
The xkbcomp keymap compiler converts a description of an XKB keymap into one
of several output formats. Its most common use is to create a compiled
keymap file that can be read directly by XKB-capable X servers or utilities.

%prep
%setup -a 0

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xkbcomp.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.5.0-4
- Replace the TODO summary/description and record the verified license
  (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.5.0-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.5.0-2
- Split devel payload into xkbcomp-devel (size audit)

# let's skip this for now

