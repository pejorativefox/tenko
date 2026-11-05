Name:       libusb
Version:    1.0.30
Release:    4
Summary:    Cross-platform USB device access library
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    libusb-1.0.30.tar.bz2

%description
libusb is a library for USB device access from Linux, macOS, Windows,
OpenBSD/NetBSD, Haiku, Solaris userspace and WebAssembly via WebUSB. It is
written in C and provides a portable API for applications that communicate
with USB hardware.

%prep
%setup -a 0

%build
%configure 
%make_build

%install
%make_install

%files -f %{_sourcedir}/libusb.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.30-4
- Replace the TODO summary/description and record the verified license
  (LGPL-2.1-or-later): libusb/core.c (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.0.30-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.0.30
- Sync with BLFS r13.1 (1.0.23)

# let's skip this for now
