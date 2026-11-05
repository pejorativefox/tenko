Name:       freetype
Version:    2.15.0
Release:    2
Summary:    TrueType font library
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: harfbuzz >= 8.1.1

Provides: pkgconfig(freetype2)
%description
The FreeType2 package contains a library which allows applications to properly render TrueType fonts. 

%prep
%setup -q

%build
sed -ri "s:.*(AUX_MODULES.*valid):\1:" modules.cfg &&

sed -r "s:.*(#.*SUBPIXEL_RENDERING) .*:\1:" \
    -i include/freetype/config/ftoption.h  &&
%configure --enable-freetype-config --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/freetype.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.15.0-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.15.0-1
- Sync with BLFS r13.1

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.14.3-2
- Split devel payload into freetype-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.14.3
- Sync with BLFS r13.1 (2.13.1)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2.13.1-1
- Version bump
