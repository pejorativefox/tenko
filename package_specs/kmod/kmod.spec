Name:       kmod
Version:    34.2
Release:    1
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

%files
/usr/bin/kmod
/usr/bin/lsmod
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
* Fri Oct 30 2026 browneye <build@browneye.invalid> 34.2
- Sync with LFS r13.1

# let's skip this for now
