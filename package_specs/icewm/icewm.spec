Name:       icewm
Version:    4.1.0
Release:    3
Summary:    A small win9x like window manager
License:    LGPL-2.0-or-later
URL:        https://ice-wm.org/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: imlib2
BuildRequires: pulseaudio
BuildRequires: fribidi
BuildRequires: git
BuildRequires: libice
BuildRequires: libsm
BuildRequires: libx11
BuildRequires: libxcomposite
BuildRequires: libxcursor
BuildRequires: libxdamage
BuildRequires: libxext
BuildRequires: libxfixes
BuildRequires: libxft
BuildRequires: libxinerama
BuildRequires: libxrandr
BuildRequires: libxrender
BuildRequires: libxres
BuildRequires: xorgproto
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: harfbuzz
BuildRequires: libXdmcp
BuildRequires: libpng
BuildRequires: libxau
BuildRequires: libxcb

%description
A small win9x like window manager

%prep
%setup

%build
mkdir build
pushd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr -DICESOUND=none
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
%make_install
popd
# CMake installs the playground translations under the absolute build path.
rm -rf %{buildroot}%{_builddir}
rmdir -p --ignore-fail-on-non-empty "$(dirname %{buildroot}%{_builddir})"

%files -f %{_sourcedir}/icewm.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 4.1.0-3
- Stop shipping the playground translations that CMake installed under
  the absolute build directory (/out/build/...).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.1.0-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.0-or-later): COPYING, GNU Library GPL v2, plus src/MwmUtil.h "or any later version" (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 4.1.0-1
- Sync with the base set

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 3.4.1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.6.5
- Initial RPM

