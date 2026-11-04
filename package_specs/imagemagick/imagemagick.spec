Name:       imagemagick
Version:    7.1.2
Release:    2
Summary:    OSS image manipulation toolkit
License:    GPL3
Prefix:     /usr
Source0:    ImageMagick-7.1.2-13.tar.gz
%description
ImageMagick is a free, open-source software suite, used for editing and manipulating digital images.

%package doc
Summary:    imagemagick documentation
Requires:   imagemagick = %{version}-%{release}

%description doc
Documentation for imagemagick.

%prep
%setup -q -n ImageMagick-7.1.2-13

%build
%configure  --sysconfdir=/etc \
            --enable-hdri     \
            --with-modules    \
            --with-perl       \
            --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/imagemagick.filelist
%files doc -f %{_sourcedir}/imagemagick-doc.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 7.1.2-2
- Split doc payload into imagemagick-doc (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 7.1.2
- Sync with BLFS r13.1 (7.1.1)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 7.1.1-1
- Version bump

