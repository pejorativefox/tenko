Name:       glew
Version:    2.3.1
Release:    2
Summary:    GLEW is the OpenGL Extension Wrangler Library. 
License:    BSD-3-Clause AND MIT
Source0:    %{name}-%{version}.tgz
Prefix:     /usr

%description
GLEW is the OpenGL Extension Wrangler Library. 

%prep
%setup

%build
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/local/include/GL/eglew.h
/usr/local/include/GL/glew.h
/usr/local/include/GL/glxew.h
/usr/local/include/GL/wglew.h
/usr/local/lib/pkgconfig/glew.pc
/usr/local/lib64/libGLEW.a
/usr/local/lib64/libGLEW.so
/usr/local/lib64/libGLEW.so.2.3
/usr/local/lib64/libGLEW.so.2.3.1

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.3.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (BSD-3-Clause AND MIT): LICENSE.txt (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.3.1-1
- Sync with BLFS r13.1

* Wed Aug 19 2020 Chris Statzer <chris.statzer@qq.com> 2.1.0
- Initial RPM

