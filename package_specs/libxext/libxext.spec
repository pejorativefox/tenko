Name:       libxext
Version:    1.3.7
Release:    1
Summary:    Library for common extensions to the X11 protocol
License:    GPL3
Prefix:     /usr
Source0:    libXext-%{version}.tar.xz
%description
Library for common extensions to the X11 protocol

%prep
%setup -q -n libXext-%{version}


%build
%configure ICE_LIBS=-lpthread
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxext.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.3.7
- Sync with BLFS r13.1 (1.3.5)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.3.5-1
- Version bump
