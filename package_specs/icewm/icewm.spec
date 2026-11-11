Name:       icewm
Version:    4.1.0
Release:    2
Summary:    A small win9x like window manager
License:    LGPL-2.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: imlib2
BuildRequires: pulseaudio

%description
A small win9x like window manager

%prep
%setup

%build
mkdir build
pushd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
%make_install
popd 

%files -f %{_sourcedir}/icewm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.1.0-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.0-or-later): COPYING, GNU Library GPL v2, plus src/MwmUtil.h "or any later version" (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 4.1.0-1
- Sync with the base set

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 3.4.1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.6.5
- Initial RPM

