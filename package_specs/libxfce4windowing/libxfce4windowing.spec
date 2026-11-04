Name:       libxfce4windowing
Version:    4.20.7
Release:    3
Summary:    Abstraction library for windowing concepts
License:    LGPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: libwnck

%description
Libxfce4windowing is an abstraction library that attempts to present windowing concepts (screens, toplevel windows, workspaces, etc.) in a windowing-system-independent manner.

%package doc
Summary:    libxfce4windowing documentation
Requires:   libxfce4windowing = %{version}-%{release}

%description doc
Documentation for libxfce4windowing.

%package devel
Summary:    libxfce4windowing development files
Requires:   %{name}-gir = %{version}-%{release}
Requires:   libxfce4windowing = %{version}-%{release}

%description devel
Development files for libxfce4windowing.

%prep
%setup

%build
%configure --enable-x11 --disable-wayland --disable-debug
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install


%package gir
Summary:    GObject Introspection data for libxfce4windowing
License:    LGPL
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for libxfce4windowing, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the -devel package.

%files -f %{_sourcedir}/libxfce4windowing.filelist
%files doc -f %{_sourcedir}/libxfce4windowing-doc.filelist
%files devel -f %{_sourcedir}/libxfce4windowing-devel.filelist
%files gir -f %{_sourcedir}/libxfce4windowing-gir.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20.7-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.7-2
- Split doc, devel payload into libxfce4windowing-doc, libxfce4windowing-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.7
- Sync with BLFS r13.1 (4.19.2)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.2
- Initial RPM

