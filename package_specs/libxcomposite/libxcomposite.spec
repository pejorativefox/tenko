Name:       libxcomposite
Version:    0.4.7
Release:    1
Summary:    Xorg composite ext library
License:    GPL3
Prefix:     /usr
Source0:    libXcomposite-%{version}.tar.xz
BuildRequires: libxfixes

%description
Xlib-based client library for the Composite extension to the X11 protocol.

%prep
%setup -q -n libXcomposite-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxcomposite.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.4.7
- Sync with BLFS r13.1 (0.4.6)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.4.6-1
- Version bump
