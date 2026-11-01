Name:       at-spi2-core
Version:    2.62.0.1
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
Provides: pkgconfig(atspi-2)

%description
TODO

%prep
%setup

%build
mkdir build
pushd build
meson setup ..                  \
      --prefix=/usr             \
      --buildtype=release       \
      -D gtk2_atk_adaptor=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/at-spi2-core.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.60.6
- Sync with BLFS r13.1 (2.48.3)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 3.30.1
- Initial RPM


