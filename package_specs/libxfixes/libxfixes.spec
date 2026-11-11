Name:       libxfixes
Version:    6.0.2
Release:    4
Summary:    Xlib-based library for the XFIXES Extension.
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxfixes
Prefix:     /usr
Source0:    libXfixes-%{version}.tar.xz
%description
Xlib-based library for the XFIXES Extension.

%package static
Summary:    libxfixes static libraries
Requires:   libxfixes = %{version}-%{release}

%description static
Static libraries for libxfixes.

%prep
%setup -q -n libXfixes-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxfixes.filelist
%files static -f %{_sourcedir}/libxfixes-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 6.0.2-4
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 6.0.2-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 6.0.2-2
- Split devel, static payload into libxfixes-devel, libxfixes-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 6.0.2
- Sync with 6.0.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 6.0.1-1
- Version bump
