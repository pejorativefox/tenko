Name:       libxinerama
Version:    1.1.6
Release:    4
Summary:    Xlib API for Xinerama extension to X11 Protocol
License:    MIT
Prefix:     /usr
Source0:    libXinerama-%{version}.tar.xz
%description
Xlib API for Xinerama extension to X11 Protocol

%package static
Summary:    libxinerama static libraries
Requires:   libxinerama = %{version}-%{release}

%description static
Static libraries for libxinerama.

%prep
%setup -q -n libXinerama-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxinerama.filelist
%files static -f %{_sourcedir}/libxinerama-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.6-4
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.6-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.6-2
- Split devel, static payload into libxinerama-devel, libxinerama-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.1.6
- Sync with BLFS r13.1 (1.1.5)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.5-1
- Version bump
