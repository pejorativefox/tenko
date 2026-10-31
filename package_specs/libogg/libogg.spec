Name:       libogg
Version:    1.3.6
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    libogg-1.3.6.tar.xz


%description
TODO

%prep
%setup -q

%build
%configure  --prefix=/usr    \
            --disable-static \
            --docdir=/usr/share/doc/libogg-1.3.3
%make_build

%install    
rm -rf %{buildroot}
%make_install

%files
/usr/

%changelog
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.3.3-1
- Version bump

