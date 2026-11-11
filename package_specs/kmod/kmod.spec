Name:       kmod
Version:    34.3
Release:    3
Summary:    Kernel module utilities
License:    LGPL-2.1-or-later AND GPL-2.0-or-later
URL:        https://git.kernel.org/pub/scm/utils/kernel/kmod/kmod.git
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The Kmod package contains libraries and utilities for loading kernel modules 

%prep
%setup -q

%build
mkdir -p build
pushd build
meson setup --prefix=/usr --libdir=%{_libdir} -D manpages=false -D openssl=disabled ..
ninja -j%{_smp_build_ncpus}
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

mkdir -pv %{buildroot}/usr/sbin

for target in depmod insmod modinfo modprobe rmmod; do
  ln -sfv ../bin/kmod %{buildroot}/usr/sbin/$target
done

ln -sfv kmod %{buildroot}/usr/bin/lsmod

# The kernel is built with CONFIG_MODPROBE_PATH="/usr/bin/modprobe" (from the
# Fedora config).  Module autoloading for filesystems and socket families goes
# through that path, so it must exist even though the utilities live in
# /usr/sbin.
ln -sfv kmod %{buildroot}/usr/bin/modprobe

%files -f %{_sourcedir}/kmod.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 34.3-3
- Record the verified license (LGPL-2.1-or-later AND GPL-2.0-or-later): README.md and libkmod/libkmod.c (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 34.3-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 34.3-1
- Update to 34.3 (current upstream version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 34.2-3
- Split devel payload into kmod-devel (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 34.2-2
- Install /usr/bin/modprobe.  The kernel's CONFIG_MODPROBE_PATH points there;
  without it, request_module() autoloading fails (e.g. mounting
  binfmt_misc), while an explicit "modprobe" still works.

* Fri Oct 30 2026 browneye <build@browneye.invalid> 34.2
- Sync with the base set

# let's skip this for now
