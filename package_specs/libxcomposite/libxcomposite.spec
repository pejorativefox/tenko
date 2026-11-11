Name:       libxcomposite
Version:    0.4.7
Release:    4
Summary:    Xorg composite ext library
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxcomposite
Prefix:     /usr
Source0:    libXcomposite-%{version}.tar.xz
BuildRequires: libxfixes
BuildRequires: libx11
BuildRequires: util-macros
BuildRequires: xorgproto

%description
Xlib-based client library for the Composite extension to the X11 protocol.

%package static
Summary:    libxcomposite static libraries
Requires:   libxcomposite = %{version}-%{release}

%description static
Static libraries for libxcomposite.

%prep
%setup -q -n libXcomposite-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxcomposite.filelist
%files static -f %{_sourcedir}/libxcomposite-static.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.4.7-4
- Record the verified license (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.4.7-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.4.7-2
- Split devel, static payload into libxcomposite-devel, libxcomposite-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.4.7
- Sync with 0.4.6

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.4.6-1
- Version bump
