Name:       imagemagick
Version:    7.1.2
Release:    3
Summary:    OSS image manipulation toolkit
License:    ImageMagick
URL:        https://imagemagick.org/
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
# Modules are loaded through libltdl, which looks for the companion .la
# files.  rpm's brp-remove-la-files deletes every .la from the buildroot,
# so the installed ImageMagick could not load a single coder (PNG, JPEG,
# ...); configure still reported the delegates as present.  Build the
# coders into libMagickCore instead.
%configure  --sysconfdir=/etc \
            --enable-hdri     \
            --without-modules \
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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 7.1.2-3
- Build the coders into libMagickCore (--without-modules).  The package
  was built with --with-modules, so ImageMagick looked for the coders
  through libltdl, which needs the companion .la file; rpm's
  brp-remove-la-files strips those, and no coder (PNG, JPEG, ...) could
  be loaded at all.
- Record the real license (ImageMagick) instead of the GPL3 placeholder.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 7.1.2-2
- Split doc payload into imagemagick-doc (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 7.1.2
- Sync with 7.1.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 7.1.1-1
- Version bump

