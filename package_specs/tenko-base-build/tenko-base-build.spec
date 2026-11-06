Name:       tenko-base-build
Version:    13.1
Release:    3
# Tenko rename compatibility (issue #22).
Obsoletes: browneye-base-build < 13.1-3
Provides: browneye-base-build = %{version}-%{release}
Summary:    Tenko Linux build environment (runtime base + toolchain)
License:    MIT
Prefix:     /usr

# tenko-base-runtime (runtime half) plus everything needed to compile
# and package RPMs, including headers and static libraries.  Provision a
# build container/image with this meta instead of the monolithic
# tenko-base.
Requires:   tenko-base-runtime
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
Requires:   tenko-rpm-config
Requires:   groff
Requires:   man-db
Requires:   man-pages

%description
The Tenko base build environment: tenko-base-runtime plus the
GCC toolchain (including the LTO parts and static libraries), binutils,
the autotools, gettext tools, texinfo, tcl/expect/dejagnu,
meson/ninja/cmake, kernel headers, glibc locale sources for localedef,
the Python build backends and the RPM packaging macros.  Development
headers and .pc files ship in the runtime packages themselves.

Use this profile for a build container or CI image.  tenko-base stays
available unchanged for existing installs.

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/tenko
touch %{buildroot}/usr/share/tenko/base-build

%post
# Remove the old marker directory left by browneye-base-build.
rm -f /usr/share/browneye/base-build
rmdir /usr/share/browneye 2>/dev/null || true

%files
/usr/share/tenko/base-build

%changelog
* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-3
- Rename browneye-base-build to tenko-base-build and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 13.1-2
- Drop the gcc-devel, binutils-devel, glibc-devel, openssl-devel and
  perl-devel requirements: the -devel subpackages are gone and their
  payload now ships in the runtime packages (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-1
- New build profile: browneye-base-runtime + GCC/binutils toolchain,
  autotools, gettext/texinfo, meson/ninja/cmake, devel and static
  subpackages, Python build backends (size audit B3/B4)
