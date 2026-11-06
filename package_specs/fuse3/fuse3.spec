Name:       fuse3
Version:    3.18.3
Release:    1
Summary:    Filesystem in Userspace 3
License:    GPL-2.0-only AND LGPL-2.1-only
URL:        https://github.com/libfuse/libfuse
Source0:    fuse-%{version}.tar.gz
Prefix:     /usr

%description
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the Linux kernel.

%prep
%setup -q -n fuse-%{version}
sed -i '/^udev/,$ s/^/#/' util/meson.build

%build
mkdir build
pushd build
meson setup --prefix=/usr --buildtype=release ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files
/usr/bin/fusermount3
/usr/include/fuse3/cuse_lowlevel.h
/usr/include/fuse3/fuse.h
/usr/include/fuse3/fuse_common.h
/usr/include/fuse3/fuse_log.h
/usr/include/fuse3/fuse_lowlevel.h
/usr/include/fuse3/fuse_opt.h
/usr/include/fuse3/libfuse_config.h
/usr/lib64/libfuse3.so
/usr/lib64/libfuse3.so.3.18.3
/usr/lib64/libfuse3.so.4
/usr/lib64/pkgconfig/fuse3.pc
/usr/sbin/mount.fuse3
/usr/share/man/man1/fusermount3.1.gz
/usr/share/man/man8/mount.fuse3.8.gz

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.18.3-1
- New package, required by xdg-desktop-portal
