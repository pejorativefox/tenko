Name:       kmod
Version:    34.2
Release:    2
Summary:    Kernel module utilities
License:    GPL3
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

%files
/usr/bin/kmod
/usr/bin/lsmod
/usr/bin/modprobe
/usr/sbin/depmod
/usr/sbin/insmod
/usr/sbin/modinfo
/usr/sbin/modprobe
/usr/sbin/rmmod
/usr/sbin/lsmod
/usr/include/libkmod.h
/usr/lib64/libkmod.so
/usr/lib64/libkmod.so.2
/usr/lib64/libkmod.so.2.5.1
/usr/lib64/pkgconfig/libkmod.pc
/usr/share/bash-completion/completions/
/usr/share/fish/vendor_functions.d/
/usr/share/zsh/site-functions/
/usr/share/pkgconfig/kmod.pc


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 34.2-2
- Install /usr/bin/modprobe.  The kernel's CONFIG_MODPROBE_PATH points there;
  without it, request_module() autoloading fails (e.g. mounting
  binfmt_misc), while an explicit "modprobe" still works.

* Fri Oct 30 2026 browneye <build@browneye.invalid> 34.2
- Sync with LFS r13.1

# let's skip this for now
