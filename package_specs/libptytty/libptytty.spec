Name:       libptytty
Version:    2.0
Release:    1
Summary:    OS independent and secure pty/tty and utmp/wtmp/lastlog handling library
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
libptytty is an OS independent and secure pty/tty and utmp/wtmp/lastlog
handling library, used by rxvt-unicode.

%prep
%setup -q

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_BUILD_TYPE=Release  \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D PT_UTMP_FILE=/run/utmp    ..
make
popd

%install
rm -rf %{buildroot}
pushd build
make DESTDIR=%{buildroot} install
popd

%files
/usr/include/libptytty.h
/usr/lib64/libptytty.so
/usr/lib64/libptytty.so.0
/usr/lib64/pkgconfig/libptytty.pc
/usr/share/man/man3/libptytty.3.gz

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.0-1
- New package: BLFS r13.1 build, required by rxvt-unicode 9.31
