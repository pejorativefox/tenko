Name:       libxdamage
Version:    1.1.7
Release:    1
Summary:    X Damage Extension library
License:    GPL3
Prefix:     /usr
Source0:    libXdamage-%{version}.tar.xz
%description
X Damage Extension library

%prep
%setup -q -n libXdamage-%{version}


%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxdamage.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.1.7
- Sync with BLFS r13.1 (1.1.6)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.6-1
- Version bump
