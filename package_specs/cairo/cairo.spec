Name:       cairo
Version:    1.18.4
Release:    1
Summary:    2D graphics library
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: pkgconfig(freetype2)
BuildRequires: pkgconfig(xext)
BuildRequires: pkgconfig(xcb-render)
BuildRequires: pkgconfig(xrender)

%description
Cairo is a 2D graphics library with support for multiple output devices.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/cairo.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.18.4
- Sync with BLFS r13.1 (1.17.6)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.17.6-1
- Version bump
