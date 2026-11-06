Name:       webp
Version:    1.6.0
Release:    1
Summary:    A new image format for the Web
License:    Apache 2
Source0:    lib%{name}-%{version}.tar.gz
Prefix:     /usr

%description
A new image format for the Web

%prep
%setup -n lib%{name}-%{version}

%build
%configure \
    --enable-libwebpmux \
    --enable-libwebpdemux \
    --enable-libwebpdecoder \
    --enable-libwebpextras \
    --enable-swap-16bit-csp \
    --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/webp.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.6.0-1
- Sync with upstream

* Sat Sep 05 2020 Chris Statzer <chris.statzer@qq.com> 1.1.0
- Initial RPM
