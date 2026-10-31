Name:       libxrandr
Version:    1.5.5
Release:    1
Summary:    Xlib Resize, Rotate and Reflection (RandR) extension library.
License:    GPL3
Prefix:     /usr
Source0:    libXrandr-%{version}.tar.xz
%description
Xlib Resize, Rotate and Reflection (RandR) extension library.

%prep
%setup -q -n libXrandr-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxrandr.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.5.5
- Sync with BLFS r13.1 (1.5.3)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.3-1
- Version bump
