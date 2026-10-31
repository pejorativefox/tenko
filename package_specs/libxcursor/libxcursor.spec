Name:       libxcursor
Version:    1.2.3
Release:    1
Summary:    Xlib-based Cursor management library
License:    GPL3
Prefix:     /usr
Source0:    libXcursor-%{version}.tar.xz
BuildRequires: libxrender

%description
Xlib-based Cursor management library

%prep
%setup -q -n libXcursor-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxcursor.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.2.3
- Sync with BLFS r13.1 (1.2.1)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.1-1
- Version bump
