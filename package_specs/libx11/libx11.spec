Name:       libx11
Version:    1.8.13
Release:    1
Summary:    X11 protocol library
License:    GPL3
Prefix:     /usr
Source0:    libX11-%{version}.tar.xz
%description
X Window System protocol client library 

%prep
%setup -q -n libX11-%{version}


%build
%configure ICE_LIBS=-lpthread
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libx11.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.8.13
- Sync with BLFS r13.1 (1.8.6)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.8.6-1
- Version bump
