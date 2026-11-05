Name:       libpeas
Version:    1.38.1
Release:    1
Summary:    libpeas is a GObject based plugins engine, and is targeted at giving every application the chance to assume its own extensibility. 
License:    GPL
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

Provides: pkgconfig(atk-2.0)
Provides: pkgconfig(atk)

%description
libpeas is a GObject based plugins engine, and is targeted at giving every application the chance to assume its own extensibility. 

%prep
%setup

%build
mkdir build
pushd build

meson setup --prefix=/usr          \
            --buildtype=release    \
            --wrap-mode=nofallback \
            -D python3=false       \
            ..
ninja
popd

%install    
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libpeas.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.38.1-1
- Sync with BLFS r13.1 (libpeas.xml)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.26.0
- Initial RPM release
