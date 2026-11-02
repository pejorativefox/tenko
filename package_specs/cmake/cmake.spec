Name:       cmake
Version:    4.4.5
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    cmake-%{version}.tar.gz



%description
TODO

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
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.4.5-1
- Update to 4.4.5 (current LFS/BLFS r13.1 trunk version).

* Wed May 13 2020 Chris Statzer <chris.statzer@qq.com> 3.17.2
- Upgrade to fix missing policys in newer version

