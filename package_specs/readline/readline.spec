Name:       readline
Version:    8.3
Release:    4
Summary:    Library for command line editing
License:    GPL-3.0-or-later
URL:        https://tiswww.case.edu/php/chet/readline/rltop.html
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The GNU Readline library provides a set of functions for use by applications that allow users to edit command lines as they are typed in.

%package doc
Summary:    readline documentation
Requires:   readline = %{version}-%{release}

%description doc
Documentation for readline.

%prep
%setup -q 

%build
sed -i '/MV.*old/d' Makefile.in
sed -i '/{OLDSUFF}/c:' support/shlib-install

%configure --prefix=/usr    \
            --disable-static \
            --with-curses    \
            --docdir=/usr/share/doc/readline-%{version} \
            --libdir=%{_libdir}

%make_build SHLIB_LIBS="-lncursesw" 

%install
rm -rf %{buildroot}
%make_install SHLIB_LIBS="-lncursesw"
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/readline.filelist
%files doc -f %{_sourcedir}/readline-doc.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 8.3-4
- Record the verified license (GPL-3.0-or-later): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 8.3-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 8.3-2
- Split doc, devel payload into readline-doc, readline-devel (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 8.3
- Sync with the base set

# let's skip this for now
