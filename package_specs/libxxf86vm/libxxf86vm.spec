Name:       libxxf86vm
Version:    1.1.7
Release:    4
Summary:    XFree86-VidMode X extension
License:    MIT
Prefix:     /usr
Source0:    libXxf86vm-%{version}.tar.xz
%description
XFree86-VidMode X extension

%package static
Summary:    libxxf86vm static libraries
Requires:   libxxf86vm = %{version}-%{release}

%description static
Static libraries for libxxf86vm.

%prep
%setup -q -n libXxf86vm-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxxf86vm.filelist
%files static -f %{_sourcedir}/libxxf86vm-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.7-4
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.7-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.7-2
- Split devel, static payload into libxxf86vm-devel, libxxf86vm-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.1.7
- Sync with BLFS r13.1 (1.1.5)

# let's skip this for now
