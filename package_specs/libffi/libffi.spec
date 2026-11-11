Name:       libffi
Version:    3.8.0
Release:    2
Summary:    Foreign Function Interface library
License:    MIT
URL:        https://sourceware.org/libffi/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The Libffi library provides a portable, high level programming interface to various calling conventions. This allows a programmer to call any function specified by a call interface description at run time.

%prep
%setup -q

%build
%configure --disable-static --with-gcc-arch=native
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libffi.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.8.0-2
- Record the verified license (MIT): LICENSE (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.8.0
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump
