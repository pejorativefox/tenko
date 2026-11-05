Name:       xkbcomp
Version:    1.5.0
Release:    3
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
TODO

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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.5.0-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.5.0-2
- Split devel payload into xkbcomp-devel (size audit)

# let's skip this for now

