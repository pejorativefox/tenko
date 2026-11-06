Name:       hwdata
Version:    0.412
Release:    2
Summary:    Hardware identification and configuration data
License:    GPL-2.0-or-later
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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.412-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): LICENSE, COPYING and pci.ids (issue #8).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 0.412-1
- Update to 0.412 (current upstream version).

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.410
- Initial package
