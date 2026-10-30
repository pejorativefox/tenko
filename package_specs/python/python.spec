%global _python_bytecompile_errors_terminate_build 0

Name:       python
Version:    3.14.7
Release:    1
Summary:    The Python programming language
License:    GPL3
Source0:    Python-%{version}.tar.xz
Prefix:     /usr

#BuildRequires: sqlite3
#BuildRequires: bzip2
#BuildRequires: openssl
#BuildRequires: gnupg

Provides: /bin/python3, /bin/python

AutoReq: no
Requires: libbz2.so.1.0()(64bit), libc.so.6()(64bit), libcrypt.so.2()(64bit), libdl.so.2()(64bit), libexpat.so.1()(64bit) libffi.so.8()(64bit) libgdbm.so.6()(64bit) libgdbm_compat.so.4()(64bit) liblzma.so.5()(64bit) liblzma.so.5(XZ_5.0)(64bit) libm.so.6()(64bit), libncursesw.so.6()(64bit) libpanelw.so.6()(64bit) libpthread.so.0()(64bit), libreadline.so.8()(64bit) libsqlite3.so.0()(64bit) libssl.so.3()(64bit), libutil.so.1()(64bit), libuuid.so.1()(64bit), libz.so.1()(64bit)

%description
The Python programming language

%prep
%setup -q -n Python-%{version}

%build
%configure  --enable-shared        \
            --with-system-expat    \
            --with-system-ffi      \
            --enable-optimizations \
            --with-platlibdir=lib64 \
            --without-static-libpython \
            --without-ensurepip
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
sed -i 's|#!/usr/bin/env python$|#!/usr/bin/env python3|' %{buildroot}/usr/lib64/python3.14/encodings/rot_13.py
ln -s python3.14 %{buildroot}/usr/bin/python

%files
/usr/bin/
/usr/include/
/usr/lib64/
/usr/share/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.14.7
- Sync with LFS r13.1

* Tue May 19 2020 Chris Statzer <chris.statzer@qq.com> 3.7.2-2
- Removed left over tests folder.
