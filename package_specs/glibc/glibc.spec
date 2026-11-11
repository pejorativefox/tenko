Name:       glibc
Version:    2.44
Release:    5
Summary:    GNU C Library
License:    LGPL-2.1-or-later AND GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

Provides: rtld(GNU_HASH)
BuildRequires: texinfo

%description
The GNU C Library is the standard system C library for all GNU systems. It
provides the system API for programs written in C and C-compatible
languages and works with the Linux kernel to implement the operating
system behavior seen by user applications.

%package i18n
Summary:    Locale source definitions for glibc
Requires:   glibc = %{version}-%{release}

%description i18n
The locale, charmaps and repertoiremap source definitions under
/usr/share/i18n.  Install this package to run localedef and generate
locales at runtime.

%package doc
Summary:    Documentation for glibc
License:    GFDL-1.3-or-later

%description doc
Info documentation for the GNU C library.

%package locales
Summary:    Locale data for glibc
Requires:   glibc = %{version}-%{release}

%description locales
A curated set of compiled locale definitions, installed as
/usr/lib/locale/locale-archive: C, POSIX, C.UTF-8 and the UTF-8 variants
of the most widely used languages (English, German, French, Spanish,
Italian, Brazilian Portuguese, Russian, Japanese, Korean and both
Chinese scripts).  The C/POSIX locales are built into glibc itself.

Every other locale from glibc's localedata/SUPPORTED is provided by the
optional glibc-locales-extra package as per-locale directories.  glibc
consults the archive first and falls back to those directories, so the
two packages compose and neither owns a file the other one ships.

%package locales-extra
Summary:    Complete locale data for glibc (all supported locales)
Requires:   glibc-locales = %{version}-%{release}

%description locales-extra
Every locale listed in glibc's localedata/SUPPORTED that is not part of
the curated glibc-locales archive, as per-locale directories below
/usr/lib/locale.  Together with glibc-locales this restores the full
locale coverage of the former 222 MB archive.

This package is additive: it does not replace /usr/lib/locale/locale-archive
and can be erased at any time without leaving a broken system (the curated
archive and everything tenko-base depends on stays installed).

%prep
%setup -q

%build
export CFLAGS="-O2 -g"
export CXXFLAGS="-O2 -g"
export LDFLAGS=""
patch -Np1 -i %{_sourcedir}/glibc-fhs-1.patch
patch -Np1 -i %{_sourcedir}/glibc-2.44-upstream_fixes-3.patch

mkdir build
pushd build
../configure --prefix=/usr                            \
             --disable-werror                         \
             --disable-nscd                           \
             --without-selinux                        \
             libc_cv_slibdir=/usr/lib64               \
             --enable-kernel=5.10                     \
             --enable-stack-protector=strong
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
sed '/test-installation/s@$(PERL)@echo not running@' -i ../Makefile
make -j%{_smp_build_ncpus} install_root=%{buildroot} install
if [ -d %{buildroot}/sbin ]; then mkdir -p %{buildroot}/usr/sbin; mv %{buildroot}/sbin/* %{buildroot}/usr/sbin/; rmdir %{buildroot}/sbin; fi
sed '/RTLDLIST=/s@/usr@@g' -i %{buildroot}/usr/bin/ldd
popd

# Locale data split (2026-10 size audit).
#
# glibc-locales gets a curated archive; every other locale from
# localedata/SUPPORTED is installed as a per-locale directory tree that
# belongs to glibc-locales-extra.  glibc looks a locale up in the archive
# first and falls back to /usr/lib/locale/<locale>/LC_*, so the directory
# tree works alongside the archive and the packages share no path.  Using
# directories for the opt-in package means -extra is purely additive: it
# can be installed or erased without touching the base archive or the
# tenko-base requirement on glibc-locales.
#
# Both sets are compiled in this one %install pass with the just-built
# localedef (run through the just-built loader) and the just-installed
# locale sources, exactly like glibc's own localedata/Makefile does.
I18NDIR=%{buildroot}/usr/share/i18n
LOCALEDEF="%{buildroot}/usr/lib64/ld-linux-x86-64.so.2 --library-path %{buildroot}/usr/lib64 %{buildroot}/usr/bin/localedef"
BUILDROOT_LOCALE=%{buildroot}
export LC_ALL=C I18NPATH="$I18NDIR" GCONV_PATH="%{buildroot}/usr/lib/gconv" LOCALEDEF BUILDROOT_LOCALE

CURATED="C.UTF-8 en_US.UTF-8 en_GB.UTF-8 de_DE.UTF-8 fr_FR.UTF-8 es_ES.UTF-8 it_IT.UTF-8 pt_BR.UTF-8 ru_RU.UTF-8 ja_JP.UTF-8 ko_KR.UTF-8 zh_CN.UTF-8 zh_TW.UTF-8"

mkdir -p %{buildroot}/usr/lib/locale
for l in $CURATED; do
    $LOCALEDEF -A %{_builddir}/%{name}-%{version}/intl/locale.alias \
        -i "$I18NPATH/locales/${l%%.*}" -f "${l#*.}" \
        --prefix=%{buildroot} "$l"
done

# List the SUPPORTED locales that are not in the curated archive.
sed -e 's/#.*//' -e 's/\\$//' %{_builddir}/%{name}-%{version}/localedata/SUPPORTED \
  | awk '{print $1}' | grep / \
  | while read -r entry; do
        locale=${entry%/*}
        case " $CURATED " in *" $locale "*) continue ;; esac
        printf '%s\n' "$entry"
    done > %{_builddir}/extra-locales.list
echo "-extra locales: $(wc -l < %{_builddir}/extra-locales.list)"

cat > %{_builddir}/compile-locale-dir.sh << "EOF"
#!/bin/sh
set -e
entry=$1
charset=${entry##*/}
locale=${entry%/*}
input=$(printf '%s\n' "$locale" | sed 's/\([^.]*\)[^@]*\(.*\)/\1\2/')
flags=--no-archive
case $charset in SHIFT_JIS|SHIFT_JISX0213) flags="$flags --no-warnings=ascii" ;; esac
exec $LOCALEDEF $flags -i "$I18NPATH/locales/$input" -f "$charset" \
     --prefix="$BUILDROOT_LOCALE" "$locale"
EOF
chmod +x %{_builddir}/compile-locale-dir.sh
xargs -r -n1 -P%{_smp_build_ncpus} %{_builddir}/compile-locale-dir.sh \
    < %{_builddir}/extra-locales.list

# The -extra filelist is static; fail the build instead of silently
# leaving compiled locales out of the package if the tree ever changes.
( cd %{buildroot} && find usr/lib/locale -mindepth 1 \( -type f -o -type l \) \
    -printf '/%p\n' | grep -v '^/usr/lib/locale/locale-archive$' \
    | LC_ALL=C sort ) > %{_builddir}/extra-files.actual
grep -v '^%dir ' %{_sourcedir}/glibc-locales-extra.filelist \
    | LC_ALL=C sort > %{_builddir}/extra-files.expected
diff -u %{_builddir}/extra-files.expected %{_builddir}/extra-files.actual

cp -v nscd/nscd.conf %{buildroot}/etc/nscd.conf
mkdir -pv %{buildroot}/var/cache/nscd
touch %{buildroot}/var/cache/nscd/.keep

mkdir -pv %{buildroot}/etc
cat > %{buildroot}/etc/nsswitch.conf << "EOF"
# Begin /etc/nsswitch.conf

passwd: files
group: files
shadow: files

hosts: files dns
networks: files

protocols: files
services: files
ethers: files
rpc: files

# End /etc/nsswitch.conf
EOF

mkdir -pv %{buildroot}/etc/ld.so.conf.d/
cat >> %{buildroot}/etc/ld.so.conf << "EOF"
# Add an include directory
include /etc/ld.so.conf.d/*.conf
/usr/local/lib
/opt/lib

EOF
mkdir -pv %{buildroot}/etc/ld.so.conf.d
touch %{buildroot}/etc/ld.so.conf.d/.keep

%files -f %{_sourcedir}/glibc.filelist
%exclude /usr/lib/locale/
%files i18n -f %{_sourcedir}/glibc-i18n.filelist
%files doc -f %{_sourcedir}/glibc-doc.filelist

%files locales
%dir /usr/lib/locale
/usr/lib/locale/locale-archive

%files locales-extra -f %{_sourcedir}/glibc-locales-extra.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.44-5
- Replace the TODO summary/description and record the verified license
  (LGPL-2.1-or-later AND GPL-2.0-or-later): COPYING.LESSERv2, COPYINGv2 (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.44-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.44-3
- Split locale data (2026-10 size audit): glibc-locales now ships a curated
  locale-archive (C, POSIX, C.UTF-8 and the UTF-8 variants of en_US,
  en_GB, de_DE, fr_FR, es_ES, it_IT, pt_BR, ru_RU, ja_JP, ko_KR, zh_CN
  and zh_TW) instead of all 886 localedata/SUPPORTED entries (~222 MB).
- New glibc-locales-extra carries every remaining SUPPORTED locale as
  per-locale directories, so it is additive: erasing it keeps the base
  archive and browneye-base's dependency intact, and no path is owned by
  both packages.
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.44-2
- Split development files, locale sources and documentation into
  glibc-devel, glibc-i18n and glibc-doc; the runtime package keeps the
  loader, versioned libraries, gconv and system configuration
  (size audit §7)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.44
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.44
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 2.38
- Version bump
