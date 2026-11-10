Name:       radeontop
Version:    1.4
Release:    1
Summary:    GPU utilization viewer for AMD Radeon devices
License:    GPL-3.0-only
URL:        https://github.com/clbr/radeontop
Source0:    %{name}-%{version}.tar.gz
BuildRequires: gcc, make, pkgconf, gettext
BuildRequires: libdrm, libpciaccess, ncurses, libxcb
Prefix:     /usr

%description
radeontop is a console tool that shows AMD/ATI Radeon GPU utilization: the
total activity percentage plus the individual blocks (graphics, compute,
DMA, UVD/VCE and the memory controllers).  It reads the GPU registers
through /dev/dri/cardN (or /dev/mem), so it needs access to the graphics
device.

The package is built with the amdgpu ioctl reporting, X11/XCB support for
unprivileged use under Xorg, and translations.

%prep
%setup -q

# The GitHub archive is not a git checkout, so getver.sh cannot derive a
# version string.  Write the header it would generate.
cat > include/version.h <<'EOF'
#ifndef VER_H
#define VER_H

#define VERSION "%{version}"

#endif
EOF

%build
# The Makefile regenerates include/version.h from git; with a .git directory
# present (and older than the header) it keeps the version written above.
mkdir -p .git
touch include/version.h
%make_build xcb=1 amdgpu=1 nls=1

%install
rm -rf %{buildroot}
make install \
    DESTDIR=%{buildroot} \
    PREFIX=/usr \
    LIBDIR=%{_lib}

%files -f %{_sourcedir}/radeontop.filelist

%changelog
* Tue Nov 10 2026 browneye <build@browneye.invalid> 1.4-1
- Initial package.  Radeontop is not in the base set.
- Version 1.4 is the latest stable upstream tag (2021-11-24); upstream
  has no GitHub releases and no newer tag.  Newer commits on master add
  GPU IDs but are not a release, so they are not packaged.
- Source: https://github.com/clbr/radeontop/archive/refs/tags/v1.4.tar.gz
  md5 a6402ee26ebcdc4177725a1299a11a0d
  sha256 2c1e2aace1a749d8e4530047ce245004e0f7d1d32a99037917e03d83e60f7ad1
- Build with amdgpu, XCB and NLS enabled; the XCB helper library goes to
  /usr/lib64.
