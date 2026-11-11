Name:       zip
Version:    3.0
Release:    1
Summary:    Info-ZIP zip
License:    Info-ZIP
URL:        https://infozip.sourceforge.net/Zip.html
Prefix:     /usr
Source0:    zip30.tar.gz

%description
Zip is a compression and file packaging utility for Unix, VMS, MSDOS,
OS/2, Windows NT, Minix, Atari and Macintosh.  Zip is analogous to a
combination of tar and compress: it creates a compressed archive of one or
more files, with per-file compression, and is the standard tool for
producing .zip archives on Unix.  Companion utilities zipcloak, zipnote and
zipsplit encrypt, annotate and split archives.

%prep
%setup -q -n zip30

%build
# The upstream sources are K&R C.  GCC 16 defaults to gnu23, where "f()"
# means "f(void)" and every old-style definition is a hard error, so compile
# in gnu89 mode (the same fix applies here).
make -f unix/Makefile generic CC="gcc -std=gnu89"

%install
rm -rf %{buildroot}
make prefix=%{buildroot}/usr MANDIR=%{buildroot}/usr/share/man/man1 \
    -f unix/Makefile install

%files -f %{_sourcedir}/zip.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.0-1
- Ship zip.  The spec was a stub (Version 30, Summary TODO, %setup -a0
  re-extracting the tarball, %make_install commented out) and no zip RPM
  was ever published, so Browneye could extract archives but not create
  them.  Rebuilt from the package page: Version 3.0, generic target with
  gcc -std=gnu89 (the K&R sources do not survive GCC 16's gnu23 default),
  upstream install target, man pages included.
