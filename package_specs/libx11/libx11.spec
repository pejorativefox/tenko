Name:       libx11
Version:    1.8.14
Release:    2
Summary:    X11 protocol library
License:    GPL3
Prefix:     /usr
Source0:    libX11-%{version}.tar.xz
%description
X Window System protocol client library 

%package doc
Summary:    libx11 documentation
Requires:   libx11 = %{version}-%{release}

%description doc
Documentation for libx11.

%package static
Summary:    libx11 static libraries
Requires:   libx11 = %{version}-%{release}

%description static
Static libraries for libx11.

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
%files doc -f %{_sourcedir}/libx11-doc.filelist
%files static -f %{_sourcedir}/libx11-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.8.14-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.8.14-1
- Update to 1.8.14 (current BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.8.13-2
- Split devel, doc, static payload into libx11-devel, libx11-doc, libx11-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.8.13
- Sync with BLFS r13.1 (1.8.6)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.8.6-1
- Version bump
