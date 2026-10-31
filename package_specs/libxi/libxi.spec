Name:       libxi
Version:    1.8.3
Release:    1
Summary:    Library for the X Input Extension.
License:    GPL3
Prefix:     /usr
Source0:    libXi-%{version}.tar.xz
%description
Library for the X Input Extension.

%prep
%setup -q -n libXi-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxi.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.8.3
- Sync with BLFS r13.1 (1.8.1)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.8.1-1
- Version bump
