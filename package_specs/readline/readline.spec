Name:       readline
Version:    8.3
Release:    2
Summary:    Library for command line editing
License:    GPL3
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The GNU Readline library provides a set of functions for use by applications that allow users to edit command lines as they are typed in.

%package doc
Summary:    readline documentation
Requires:   readline = %{version}-%{release}

%description doc
Documentation for readline.

%package devel
Summary:    readline development files
Requires:   readline = %{version}-%{release}

%description devel
Development files for readline.

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
%files devel -f %{_sourcedir}/readline-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 8.3-2
- Split doc, devel payload into readline-doc, readline-devel (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 8.3
- Sync with LFS r13.1

# let's skip this for now
