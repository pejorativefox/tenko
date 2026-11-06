# Source0: https://github.com/dracut-ng/dracut-ng/archive/refs/tags/112.tar.gz
#   sha256 839d21eb4bd27bb0ee40d74c9da46df088c2e1425fcd8c3ea62b7e3a3dd28a91
#
# dracut-ng is the maintained successor to the original dracut project.
Name:       dracut
Version:    112
Release:    1
Summary:    Event-driven initramfs infrastructure
License:    GPL-2.0-or-later
URL:        https://github.com/dracut-ng/dracut
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: kmod
Requires:   cpio
Requires:   kmod

%description
dracut creates an initramfs image by copying tools and files from an
installed system and combining it with dracut modules, usually found in
/usr/lib/dracut/modules.d.

This is dracut-ng, the maintained successor to the original dracut
project.  It is used to build the Tenko initramfs for NVMe, LUKS/LVM
and other roots that are not built into the kernel.

%prep
%setup -q -n dracut-%{version}

%build
./configure \
    --prefix=/usr \
    --sysconfdir=/etc \
    --libdir=/usr/lib \
    --disable-documentation \
    --disable-dracut-cpio
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/dracut.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 112
- Replace the 2019 dracut 050 spec with dracut-ng 112
- Build without docs and without the Rust dracut-cpio helper
- Install under /usr/lib/dracut; require cpio at runtime
