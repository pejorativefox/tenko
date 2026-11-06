Name:       cmake
Version:    4.4.5
Release:    2
Summary:    Cross-platform build system generator
License:    BSD-3-Clause
Prefix:     /usr
Source0:    cmake-%{version}.tar.gz



%description
CMake is a cross-platform, open-source build system generator. It generates
native build files for a wide range of platforms and toolchains from a
single set of configuration files.

%prep
%setup


%build
sed -i '/"lib64"/s/64//' Modules/GNUInstallDirs.cmake
./bootstrap --prefix=/usr             \
            --parallel=$(nproc)       \
            --system-libs             \
            --mandir=/share/man       \
            --no-system-jsoncpp       \
            --no-system-cppdap        \
            --no-system-librhash      \
            --docdir=/share/doc/cmake-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/cmake.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.4.5-2
- Replace the TODO summary/description and record the verified license
  (BSD-3-Clause): LICENSE.rst (issue #8).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.4.5-1
- Update to 4.4.5 (current upstream version).

* Wed May 13 2020 Chris Statzer <chris.statzer@qq.com> 3.17.2
- Upgrade to fix missing policys in newer version

