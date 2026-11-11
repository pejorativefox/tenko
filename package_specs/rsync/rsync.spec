Name:       rsync
Version:    3.5.1
Release:    2
Summary:    Fast incremental file transfer tool
License:    GPL-3.0-or-later
URL:        https://rsync.samba.org/
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
rsync is a fast, versatile file-copying tool.  It is also a build
dependency of the kernel's headers_install target.

%prep
%setup -q

%build
%configure --without-included-zlib --disable-xxhash
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/rsync.filelist
