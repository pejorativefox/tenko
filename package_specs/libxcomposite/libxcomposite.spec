Name:       libxcomposite
Version:    0.4.7
Release:    2
Summary:    Xorg composite ext library
License:    GPL3
Prefix:     /usr
Source0:    libXcomposite-%{version}.tar.xz
BuildRequires: libxfixes

%description
Xlib-based client library for the Composite extension to the X11 protocol.

%package devel
Summary:    libxcomposite development files
Requires:   libxcomposite = %{version}-%{release}

%description devel
Development files for libxcomposite.

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
%files devel -f %{_sourcedir}/libxcomposite-devel.filelist
%files static -f %{_sourcedir}/libxcomposite-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.4.7-2
- Split devel, static payload into libxcomposite-devel, libxcomposite-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.4.7
- Sync with BLFS r13.1 (0.4.6)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.4.6-1
- Version bump
