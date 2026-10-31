Name:       fribidi
Version:    1.0.16
Release:    1
Summary:    GNU FriBidi 
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
Provides: pkgconfig(fribidi)

%description
The Free Implementation of the Unicode Bidirectional Algorithm.

%prep
%setup -q

%build
mkdir build-glib
pushd build-glib

meson --prefix=/usr ..
ninja
popd

%install    
rm -rf %{buildroot}
pushd build-glib
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/fribidi.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.0.16
- Sync with BLFS r13.1 (1.0.13)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.0.13-1
- Version bump
