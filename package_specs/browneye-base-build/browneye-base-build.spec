Name:       browneye-base-build
Version:    13.1
Release:    2
Summary:    Browneye Linux build environment (runtime base + toolchain)
License:    MIT
Prefix:     /usr

# browneye-base-runtime (runtime half) plus everything needed to compile
# and package RPMs, including headers and static libraries.  Provision a
# build container/image with this meta instead of the monolithic
# browneye-base.
Requires:   browneye-base-runtime
Requires:   gcc
Requires:   gcc-lto
Requires:   binutils
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
Requires:   glibc-i18n
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
GCC toolchain (including the LTO parts and static libraries), binutils,
the autotools, gettext tools, texinfo, tcl/expect/dejagnu,
meson/ninja/cmake, kernel headers, glibc locale sources for localedef,
the Python build backends and the RPM packaging macros.  Development
headers and .pc files ship in the runtime packages themselves.

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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 13.1-2
- Drop the gcc-devel, binutils-devel, glibc-devel, openssl-devel and
  perl-devel requirements: the -devel subpackages are gone and their
  payload now ships in the runtime packages (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-1
- New build profile: browneye-base-runtime + GCC/binutils toolchain,
  autotools, gettext/texinfo, meson/ninja/cmake, devel and static
  subpackages, Python build backends (size audit B3/B4)
