Name:       libexif
Version:    0.6.26
Release:    4
Summary:    EXIF metadata library
License:    LGPL2
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

%description
libexif is a library for parsing, editing and saving EXIF metadata.

%package lang
Summary:    libexif translations
Requires:   libexif = %{version}-%{release}

%description lang
Translations for libexif.

%package devel
Summary:    Development files for libexif
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in libexif; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

%prep
%setup -q

%build
%configure --disable-static --with-doc-dir=/usr/share/doc/libexif-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libexif.filelist
%files devel
%files lang -f %{_sourcedir}/libexif-lang.filelist


%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.6.26-4
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.6.26-2
- Split lang payload into libexif-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.6.26
- Initial package (BLFS r13.1)
