Name:       libxtst
Version:    1.2.5
Release:    1
Summary:    Xlib-based library for XTEST & RECORD
License:    GPL3
Prefix:     /usr
Source0:    libXtst-%{version}.tar.xz

BuildRequires: libxi

%description
Xlib-based library for XTEST & RECORD

%prep
%setup -q -n libXtst-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxtst.filelist


%changelog
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.4-1
- Version bump
