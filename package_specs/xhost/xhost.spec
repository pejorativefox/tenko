Name:       xhost
Version:    1.0.10
Release:    2
Summary:    X server access control program
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xhost
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz



%description
The xhost program is used to add and delete host names or user names to the
list allowed to make connections to the X server. It provides a rudimentary
form of privacy control and security for single-user workstations.

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

%files -f %{_sourcedir}/xhost.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.10-2
- Replace the TODO summary/description and record the verified license
  (MIT): COPYING (issue #8).

# let's skip this for now

