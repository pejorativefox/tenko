Name:       ncurses
Version:    6.6
Release:    4
Summary:    Text based user interface library
License:    X11
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
Provides:   libtinfo.so.6()(64bit)
Provides:   libncurses.so.6()(64bit)
Provides:   libform.so.6()(64bit)
Provides:   libpanel.so.6()(64bit)
Provides:   libmenu.so.6()(64bit)
Provides:   libtinfo.so.6(NCURSES_6.0)(64bit)

%description
The ncurses (new curses) library is a free software emulation of curses in System V Release 4.0 (SVr4), and more. 

%package doc
Summary:    ncurses documentation
Requires:   ncurses = %{version}-%{release}

%description doc
Documentation for ncurses.

%prep
%setup

%build
%configure  --prefix=/usr           \
            --mandir=/usr/share/man \
            --with-shared           \
            --without-debug         \
            --without-normal        \
            --with-cxx-shared       \
            --enable-pc-files       \
            --with-pkg-config-libdir=%{_libdir}/pkgconfig
%make_build

%install
rm -rf %{buildroot} dest
make DESTDIR=$PWD/dest install
sed -e 's/^#if.*XOPEN.*$/#if 1/' -i dest/usr/include/curses.h
mkdir -p %{buildroot}/usr
cp -av dest/usr/* %{buildroot}/usr/
rm -rf dest
for lib in ncurses form panel menu ; do
    ln -sfv lib${lib}w.so %{buildroot}%{_libdir}/lib${lib}.so
    ln -sfv ${lib}w.pc   %{buildroot}%{_libdir}/pkgconfig/${lib}.pc
done
ln -sfv libncursesw.so.6 %{buildroot}%{_libdir}/libncurses.so.6
ln -sfv libformw.so.6 %{buildroot}%{_libdir}/libform.so.6
ln -sfv libpanelw.so.6 %{buildroot}%{_libdir}/libpanel.so.6
ln -sfv libmenuw.so.6 %{buildroot}%{_libdir}/libmenu.so.6
ln -sfv libncursesw.so %{buildroot}%{_libdir}/libcurses.so
ln -sfv libncursesw.so.6 %{buildroot}%{_libdir}/libtinfo.so.6
ln -sfv libncursesw.so %{buildroot}%{_libdir}/libtinfo.so

# ncurses ships a separate libtinfo; readline 8.3's readline.pc declares
# "Requires.private: tinfo", so provide the matching pkg-config file.
cat > %{buildroot}%{_libdir}/pkgconfig/tinfo.pc <<'EOF'
prefix=/usr
exec_prefix=/usr
libdir=/usr/lib64
includedir=/usr/include

Name: Tinfo
Description: Terminal information library
Version: 6.6
Libs: -L${libdir} -ltinfo
Cflags: -I${includedir}
EOF

%files -f %{_sourcedir}/ncurses.filelist
%files doc -f %{_sourcedir}/ncurses-doc.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 6.6-4
- Record the verified license (X11): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 6.6-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 6.6-2
- Split doc, devel payload into ncurses-doc, ncurses-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 6.6
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 6.6
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump

* Sat Jun 17 2023 Chris Statzer <chris.statzer@gmail.com> 6.4
- Bumped version to 6.4
