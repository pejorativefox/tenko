Name:       fuse3
Version:    3.18.3
Release:    2
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

%build
mkdir build
pushd build
meson setup --prefix=/usr --buildtype=release \
    -Dutils=true             \
    -Dexamples=false         \
    -Dtests=false            \
    -Duseroot=false          \
    -Dudevrulesdir=%{_udevrulesdir} \
    -Dinitscriptdir=         \
    ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/fuse3.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 3.18.3-2
- Stop disabling the upstream install helper.  It was commenting out the
  entire tail of util/meson.build, so the package shipped fusermount3 as
  0755 and omitted /etc/fuse.conf and the 99-fuse3 udev rule.  A
  non-setuid fusermount3 makes unprivileged FUSE mounts (gvfsd-fuse,
  Thunar) fail.
- Build with -Duseroot=false and set the setuid bit explicitly in %files
  so the RPM does not try to package /dev/fuse.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.18.3-1
- New package, required by xdg-desktop-portal
