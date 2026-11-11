Name:       libxi
Version:    1.8.4
Release:    3
Summary:    Library for the X Input Extension.
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxi
Prefix:     /usr
Source0:    libXi-%{version}.tar.xz
BuildRequires: libx11
BuildRequires: libxext
BuildRequires: util-macros
BuildRequires: xorgproto
%description
Library for the X Input Extension.

%package doc
Summary:    libxi documentation
Requires:   libxi = %{version}-%{release}

%description doc
Documentation for libxi.

%package static
Summary:    libxi static libraries
Requires:   libxi = %{version}-%{release}

%description static
Static libraries for libxi.

%prep
%setup -q -n libXi-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxi.filelist
%files doc -f %{_sourcedir}/libxi-doc.filelist
%files static -f %{_sourcedir}/libxi-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.8.4-3
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.8.4-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.8.4-1
- Update to 1.8.4 (current upstream version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.8.3-2
- Split devel, doc, static payload into libxi-devel, libxi-doc, libxi-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.8.3
- Sync with 1.8.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.8.1-1
- Version bump
