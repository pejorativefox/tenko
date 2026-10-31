Name:       cmake
Version:    4.4.2
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    cmake-4.4.2.tar.gz



%description
TODO

%prep
%setup


%build
sed -i '/"lib64"/s/64//' Modules/GNUInstallDirs.cmake
./bootstrap --prefix=/usr             \
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
* Wed May 13 2020 Chris Statzer <chris.statzer@qq.com> 3.17.2
- Upgrade to fix missing policys in newer version

