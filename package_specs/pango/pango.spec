Name:       pango
Version:    1.58.2
Release:    3
Summary:    text layout library
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: fontconfig >= 2.13.1
BuildRequires: fribidi >= 1.0.13
BuildRequires: glib >= 2.76.4


%description
Pango is a library for laying out and rendering text

%package devel
Summary:    pango development files
Requires:   %{name}-gir = %{version}-%{release}
Requires:   pango = %{version}-%{release}
Provides: pkgconfig(pango)
Provides: pkgconfig(pangocairo)
Provides: pkgconfig(pangoft2)

%description devel
Development files for pango.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup --prefix=/usr            \
            --buildtype=release      \
            --wrap-mode=nofallback   \
            -D introspection=enabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*


%package gir
Summary:    GObject Introspection data for pango
License:    GPL3
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for pango, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the -devel package.

%files -f %{_sourcedir}/pango.filelist
%files devel -f %{_sourcedir}/pango-devel.filelist
%files gir -f %{_sourcedir}/pango-gir.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.58.2-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.58.2-2
- Split devel payload into pango-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.58.2
- Sync with BLFS r13.1 (1.50.14)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.50.14-1
- Version bump
