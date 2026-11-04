Name:       xkbcomp
Version:    1.5.0
Release:    2
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz



%description
TODO

%package devel
Summary:    xkbcomp development files
Requires:   xkbcomp = %{version}-%{release}

%description devel
Development files for xkbcomp.

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
%files devel -f %{_sourcedir}/xkbcomp-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.5.0-2
- Split devel payload into xkbcomp-devel (size audit)

# let's skip this for now

