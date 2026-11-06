Name:       libxrandr
Version:    1.5.5
Release:    4
Summary:    Xlib Resize, Rotate and Reflection (RandR) extension library.
License:    MIT
Prefix:     /usr
Source0:    libXrandr-%{version}.tar.xz
%description
Xlib Resize, Rotate and Reflection (RandR) extension library.

%package static
Summary:    libxrandr static libraries
Requires:   libxrandr = %{version}-%{release}

%description static
Static libraries for libxrandr.

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
%files static -f %{_sourcedir}/libxrandr-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.5.5-4
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.5.5-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.5.5-2
- Split devel, static payload into libxrandr-devel, libxrandr-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.5.5
- Sync with 1.5.3

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.3-1
- Version bump
