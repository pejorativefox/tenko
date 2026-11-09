Name:       libbytesize
Version:    2.12
Release:    1
Summary:    Library for byte-size calculations and parsing
License:    LGPL-2.1-or-later
URL:        https://github.com/storaged-project/libbytesize
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
libbytesize is a small library for working with sizes in bytes.  It parses
human-readable size strings, formats byte counts with binary and decimal
units, and performs exact arithmetic that does not lose precision on large
values.  libblockdev uses it for the btrfs and mdraid plugins.

%prep
%setup -q

%build
%configure \
    --disable-static \
    --without-python3 \
    --without-gtk-doc \
    --without-tools
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libbytesize.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 2.12-1
- Initial package at the latest stable upstream release, 2.12.
- Verified the licence as LGPL-2.1-or-later from LICENSE and the source
  file headers.
- Built without gtk-doc, the Python bindings and the command-line tools;
  libblockdev only needs the library.
