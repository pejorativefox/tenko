Name:       libexif
Version:    0.6.26
Release:    1
Summary:    EXIF metadata library
License:    LGPL2
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

%description
libexif is a library for parsing, editing and saving EXIF metadata.

%prep
%setup -q

%build
%configure --disable-static --with-doc-dir=/usr/share/doc/libexif-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libexif.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.6.26
- Initial package (BLFS r13.1)
