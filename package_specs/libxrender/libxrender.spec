Name:       libxrender
Version:    0.9.13
Release:    3
Summary:    Render Extension to the X11 protocol.
License:    MIT
Prefix:     /usr
Source0:    libXrender-%{version}.tar.xz
%description
Render Extension to the X11 protocol.

%package static
Summary:    libxrender static libraries
Requires:   libxrender = %{version}-%{release}

%description static
Static libraries for libxrender.

%prep
%setup -q -n libXrender-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxrender.filelist
%files static -f %{_sourcedir}/libxrender-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.9.13-3
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.9.13-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.9.13-1
- Update to 0.9.13 (current BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.9.12-2
- Split devel, static payload into libxrender-devel, libxrender-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.9.12
- Sync with BLFS r13.1 (0.9.11)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.9.11-1
- Version bump
