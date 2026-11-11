Name:       glew
Version:    2.3.1
Release:    2
Summary:    GLEW is the OpenGL Extension Wrangler Library. 
License:    BSD-3-Clause AND MIT
URL:        https://glew.sourceforge.net/
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

%files -f %{_sourcedir}/glew.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.3.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (BSD-3-Clause AND MIT): LICENSE.txt (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.3.1-1
- Sync with the base set

* Wed Aug 19 2020 Chris Statzer <chris.statzer@qq.com> 2.1.0
- Initial RPM

