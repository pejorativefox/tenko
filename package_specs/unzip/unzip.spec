Name:       unzip
Version:    6.0
Release:    1
Summary:    Info-ZIP unzip
License:    Info-ZIP
Prefix:     /usr
Source0:    unzip60.tar.gz
Patch0:     unzip-6.0-consolidated_fixes-1.patch
Patch1:     unzip-6.0-gcc14-1.patch

%description
UnZip is an extraction utility for archives compressed in .zip format
(also called "zipfiles").  Although highly compatible both with PKWARE's
PKZIP and PKUNZIP utilities for MS-DOS and with Info-ZIP's own Zip
program, the primary objectives have been portability and
non-MSDOS functionality.

%prep
%setup -q -n unzip60
%patch0 -p1
%patch1 -p1

%build
# The upstream sources are K&R C and declare gmtime()/localtime() with an
# empty argument list.  GCC 16 defaults to gnu23, where "f()" means "f(void)",
# so both the old prototypes and every K&R definition clash with glibc's
# headers.  Build in gnu17 mode, injecting the flag into the "flags" file
# that unix/configure generates (the generic target rebuilds with it).
make -f unix/Makefile flags
sed -i 's/CF="\([^"]*\)"/CF="\1 -std=gnu17"/' flags
eval make -f unix/Makefile unzips ACONF_DEP=flags $(cat flags)

%install
rm -rf %{buildroot}
make prefix=%{buildroot}/usr MANDIR=%{buildroot}/usr/share/man/man1 \
    -f unix/Makefile install

%files -f %{_sourcedir}/unzip.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 6.0-1
- Fix the unbuildable stub.  The consolidated patch is no longer served
  under patches/blfs/13.1, and the BLFS archive page now also requires
  unzip-6.0-gcc14-1.patch for GCC 14 and later; both are vendored in
  package_specs/unzip/files.  %setup no longer re-extracts the tarball
  with -a0, the build uses the "generic" target (generic_gcc is gone), and
  it compiles in gnu17 mode because the K&R sources do not survive GCC
  16's gnu23 default.  The install target now ships unzip, zipinfo,
  funzip, unzipsfx, zipgrep and their man pages.
