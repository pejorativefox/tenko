Name:       freeglut
Version:    3.8.0
Release:    2
Summary:    GLUT is a window system independent toolkit for writing OpenGL programs
License:    X11 AND MIT
URL:        https://freeglut.sourceforge.net/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: libglu

%description
Freeglut is intended to be a 100% compatible, completely opensourced clone of the GLUT library. GLUT is a window system independent toolkit for writing OpenGL programs, implementing a simple windowing API, which makes learning about and exploring OpenGL programming very easy.

%prep
%setup

%build
mkdir build
pushd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr        \
         -DCMAKE_INSTALL_LIBDIR=lib64       \
         -DCMAKE_BUILD_TYPE=Release         \
         -DFREEGLUT_BUILD_DEMOS=OFF         \
         -DFREEGLUT_BUILD_STATIC_LIBS=OFF   \
         -W no-author
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
%make_install
popd

%files -f %{_sourcedir}/freeglut.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.8.0-2
- Replace the legacy short licence name with the verified SPDX expression
  (X11 AND MIT): COPYING and man/LICENSE (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.8.0-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 3.4.0-1
- Version bump

* Tue Jun 16 2020 Chris Statzer <chris.statzer@qq.com> 3.2.1
- Initial RPM

