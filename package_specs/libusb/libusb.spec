Name:       libusb
Version:    1.0.30
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    libusb-1.0.30.tar.bz2

%description
TODO

%prep
%setup -a 0

%build
%configure 
%make_build

%install
%make_install

%files -f %{_sourcedir}/libusb.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.0.30
- Sync with BLFS r13.1 (1.0.23)

# let's skip this for now
