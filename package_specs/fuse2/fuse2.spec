Name:       fuse2
Version:    2.9.9
Release:    1
Summary:    Filesystem in Userspace 2 (AppImage runtime compatibility)
License:    GPL-2.0-only AND LGPL-2.1-only
URL:        https://github.com/libfuse/libfuse
Source0:    fuse-%{version}.tar.gz
Patch0:     fuse2-%{version}-closefrom-glibc.patch
Prefix:     /usr

BuildRequires: gcc
BuildRequires: make

Provides:   libfuse2 = %{version}-%{release}

%description
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the Linux kernel.

This is the FUSE 2.9 series, kept alongside fuse3 because AppImage
type-2 runtimes (libfuse.so.2) and older FUSE 2 applications still need
the FUSE 2 ABI and the unprivileged fusermount helper.  The runtime
package also contains the headers, pkg-config file and unversioned .so
links; there is no -devel subpackage.

%prep
%setup -q -n fuse-%{version}
%patch -P 0 -p1

%build
MOUNT_FUSE_PATH=/usr/sbin \
UDEV_RULES_PATH=%{_udevrulesdir} \
INIT_D_PATH=/etc/init.d \
./configure \
    --prefix=/usr \
    --libdir=%{_libdir} \
    --disable-static \
    --disable-example
%make_build

%install
rm -rf %{buildroot}
%make_install

# The upstream install hook creates /dev/fuse in the buildroot and drops a
# SysV init script.  The kernel/udev own /dev/fuse, and Tenko uses systemd;
# ship neither.
rm -rf %{buildroot}/dev
rm -f %{buildroot}/etc/init.d/fuse
rmdir %{buildroot}/etc/init.d 2>/dev/null || :
rmdir %{buildroot}/etc 2>/dev/null || :

# Upstream only chmods this with a leading '-' (errors ignored).  Make the
# setuid bit explicit and deterministic.
chmod 4755 %{buildroot}%{_bindir}/fusermount

%files -f %{_sourcedir}/fuse2.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 2.9.9-1
- New package: upstream libfuse 2.9.9, the latest stable FUSE 2 release.
  Kept for the FUSE 2 ABI (libfuse.so.2) that AppImage type-2 runtimes
  and older FUSE 2 applications dlopen; Tenko otherwise ships fuse3
  (Gitea issue #47, "AppImage support: ship FUSE 2").
- Add a patch renaming ulockmgr_server's private closefrom() helper so it
  does not clash with the closefrom() added in glibc 2.34; without it the
  package does not compile on Tenko's libc.
- Provide libfuse2 as the familiar compatibility name and ship the
  automatic libfuse.so.2()(64bit) soname provide.
- Install the unprivileged mount helper as /usr/bin/fusermount mode 4755,
  mount.fuse in /usr/sbin and the udev rule in /usr/lib/udev/rules.d.
  Do not package /dev/fuse, the SysV /etc/init.d/fuse script, or
  /etc/fuse.conf (owned by fuse3).
- No -devel subpackage: headers, .pc file and unversioned .so links stay
  in the runtime package.
