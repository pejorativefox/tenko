Name:       libusb
Version:    1.0.30
Release:    3
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    libusb-1.0.30.tar.bz2

%description
TODO

%package devel
Summary:    Development files for libusb
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in libusb; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

%prep
%setup -a 0

%build
%configure 
%make_build

%install
%make_install

%files -f %{_sourcedir}/libusb.filelist
%files devel

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.0.30-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.0.30
- Sync with BLFS r13.1 (1.0.23)

# let's skip this for now
