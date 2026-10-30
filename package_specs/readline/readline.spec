Name:       readline
Version:    8.3
Release:    1
Summary:    Library for command line editing
License:    GPL3
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The GNU Readline library provides a set of functions for use by applications that allow users to edit command lines as they are typed in.

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

%files
/usr/include/readline/chardefs.h
/usr/include/readline/history.h
/usr/include/readline/keymaps.h
/usr/include/readline/readline.h
/usr/include/readline/rlconf.h
/usr/include/readline/rlstdc.h
/usr/include/readline/rltypedefs.h
/usr/include/readline/tilde.h
/usr/lib64/libhistory.so
/usr/lib64/libhistory.so.8
/usr/lib64/libhistory.so.8.3
/usr/lib64/libreadline.so
/usr/lib64/libreadline.so.8
/usr/lib64/libreadline.so.8.3
/usr/lib64/pkgconfig/history.pc
/usr/lib64/pkgconfig/readline.pc
/usr/share/doc/
/usr/share/info/
/usr/share/man/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 8.3
- Sync with LFS r13.1

# let's skip this for now
