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

%description
The Python programming language

%prep
%setup -q -n Python-%{version}
patch -Np1 -i %{_sourcedir}/Python-3.14.7-openssl_4-1.patch

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
