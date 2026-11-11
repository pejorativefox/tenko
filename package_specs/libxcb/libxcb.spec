Name:       libxcb
Version:    1.17.0
Release:    4
Summary:    X11 client library
License:    MIT
URL:        https://xcb.freedesktop.org/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
X11 client library

%package doc
Summary:    libxcb documentation
Requires:   libxcb = %{version}-%{release}

%description doc
Documentation for libxcb.

%package static
Summary:    libxcb static libraries
Requires:   libxcb = %{version}-%{release}

%description static
Static libraries for libxcb.

%prep
%setup -q

%build 
%configure --without-doxygen
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxcb.filelist
%files doc -f %{_sourcedir}/libxcb-doc.filelist
%files static -f %{_sourcedir}/libxcb-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.17.0-4
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.17.0-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.17.0-2
- Split devel, doc, static payload into libxcb-devel, libxcb-doc, libxcb-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.17.0
- Sync with 1.15

# let's skip this for now
