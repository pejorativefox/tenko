Name:       pixman
Version:    0.46.4
Release:    4
Summary:    Low-level image libraary
License:    MIT
URL:        https://gitlab.freedesktop.org/pixman/pixman
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
%description
The Pixman package contains a library that provides low-level pixel manipulation features such as image compositing and trapezoid rasterization. 

%prep
%setup -a 0

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

%files -f %{_sourcedir}/pixman.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.46.4-4
- Record the verified license (MIT): COPYING (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.46.4-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.46.4
- Sync with 0.42.2

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.42.2
- Version bump
