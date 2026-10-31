Name:       libvorbis
Version:    1.3.7
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    libvorbis-1.3.7.tar.xz


%description
TODO

%prep
%setup -q

%build
%configure  --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.3.7
- Sync with BLFS r13.1 (1.3.6)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.3.6-1
- Version bump

