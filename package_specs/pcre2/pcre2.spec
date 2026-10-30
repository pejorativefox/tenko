Name:       pcre2
Version:    10.47
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2


%description
TODO

%prep
%setup -a 0

%build
%configure  --prefix=/usr                       \
            --docdir=/usr/share/doc/pcre2-%{version} \
            --enable-unicode                    \
            --enable-jit                        \
            --enable-pcre2-16                   \
            --enable-pcre2-32                   \
            --enable-pcre2grep-libz             \
            --enable-pcre2grep-libbz2           \
            --enable-pcre2test-libreadline      \
            --disable-static 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/pcre2-config
/usr/bin/pcre2grep
/usr/bin/pcre2test
/usr/include/pcre2.h
/usr/include/pcre2posix.h
/usr/lib64/libpcre2-16.so
/usr/lib64/libpcre2-16.so.0
/usr/lib64/libpcre2-16.so.0.15.0
/usr/lib64/libpcre2-32.so
/usr/lib64/libpcre2-32.so.0
/usr/lib64/libpcre2-32.so.0.15.0
/usr/lib64/libpcre2-8.so
/usr/lib64/libpcre2-8.so.0
/usr/lib64/libpcre2-8.so.0.15.0
/usr/lib64/libpcre2-posix.so
/usr/lib64/libpcre2-posix.so.3
/usr/lib64/libpcre2-posix.so.3.0.7
/usr/lib64/pkgconfig/libpcre2-16.pc
/usr/lib64/pkgconfig/libpcre2-32.pc
/usr/lib64/pkgconfig/libpcre2-8.pc
/usr/lib64/pkgconfig/libpcre2-posix.pc
/usr/share/doc/pcre2-%{version}/*
/usr/share/man/*

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 10.47
- Sync with LFS r13.1

# let's skip this for now

