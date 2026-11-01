Name:       browneye-base-build
Version:    13.1
Release:    1
Summary:    Browneye Linux build environment (runtime base + toolchain)
License:    MIT
Prefix:     /usr

# browneye-base-runtime (runtime half) plus everything needed to compile
# and package RPMs, including headers and static libraries.  Provision a
# build container/image with this meta instead of the monolithic
# browneye-base.
Requires:   browneye-base-runtime
Requires:   gcc
Requires:   gcc-devel
Requires:   gcc-lto
Requires:   binutils
Requires:   binutils-devel
Requires:   make
Requires:   patch
Requires:   pkgconf
Requires:   m4
Requires:   autoconf
Requires:   automake
Requires:   libtool
Requires:   bison
Requires:   flex
Requires:   gperf
Requires:   gettext
Requires:   texinfo
Requires:   tcl
Requires:   expect
Requires:   dejagnu
Requires:   ninja
Requires:   meson
Requires:   cmake
Requires:   linux-api-headers
Requires:   glibc-devel
Requires:   glibc-i18n
Requires:   openssl-devel
Requires:   perl-devel
Requires:   python-setuptools
Requires:   python-wheel
Requires:   python-flit-core
Requires:   python-packaging
Requires:   python-markupsafe
Requires:   python-jinja
Requires:   browneye-rpm-config
Requires:   groff
Requires:   man-db
Requires:   man-pages

%description
The Browneye LFS r13.1 build environment: browneye-base-runtime plus the
GCC toolchain (including the LTO parts and headers/static libraries),
binutils, the autotools, gettext tools, texinfo, tcl/expect/dejagnu,
meson/ninja/cmake, kernel headers, glibc locale sources for localedef,
the Python build backends and the RPM packaging macros.

Use this profile for a build container or CI image.  browneye-base stays
available unchanged for existing installs.

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/browneye
touch %{buildroot}/usr/share/browneye/base-build

%files
/usr/share/browneye/base-build

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-1
- New build profile: browneye-base-runtime + GCC/binutils toolchain,
  autotools, gettext/texinfo, meson/ninja/cmake, devel and static
  subpackages, Python build backends (size audit B3/B4, plan §6.I)
