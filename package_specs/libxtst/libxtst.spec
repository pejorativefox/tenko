Name:       libxtst
Version:    1.2.6
Release:    2
Summary:    Xlib-based library for XTEST & RECORD
License:    GPL3
Prefix:     /usr
Source0:    libXtst-%{version}.tar.xz

BuildRequires: libxi

%description
Xlib-based library for XTEST & RECORD

%package static
Summary:    libxtst static libraries
Requires:   libxtst = %{version}-%{release}

%description static
Static libraries for libxtst.

%prep
%setup -q -n libXtst-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxtst.filelist
%files static -f %{_sourcedir}/libxtst-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.6-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.2.6-1
- Update to 1.2.6 (current BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.5-2
- Split devel, static payload into libxtst-devel, libxtst-static (size audit)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.4-1
- Version bump
