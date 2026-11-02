Name:       hwdata
Version:    0.412
Release:    1
Summary:    Hardware identification and configuration data
License:    GPL2
Prefix:     /usr
Source0:    hwdata-%{version}.tar.gz

%description
Hardware identification and configuration data (pci.ids, usb.ids, etc.).

%prep
%setup -q

%build
./configure --prefix=/usr --disable-blacklist
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/hwdata.filelist

%changelog
* Mon Nov  2 2026 browneye <build@browneye.invalid> 0.412-1
- Update to 0.412 (current LFS/BLFS r13.1 trunk version).

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.410
- Initial package (BLFS r13.1)
