Name:       rsync
Version:    3.5.0
Release:    1
Summary:    Fast incremental file transfer tool
License:    GPL-3.0-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
rsync is a fast, versatile file-copying tool.  It is also a build
dependency of the kernel's headers_install target.

%prep
%setup -q

%build
%configure --without-included-zlib --disable-xxhash \
           --disable-lz4 --disable-zstd --disable-openssl
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/
