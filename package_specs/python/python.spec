%global _python_bytecompile_errors_terminate_build 0

Name:       python
Version:    3.14.7
Release:    2
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

%package tests
Summary:    Python standard library test suite
AutoReq:    no
Requires:   python = %{version}-%{release}

%description tests
The Python standard library test suite and its data files
(/usr/lib64/python3.14/test).  It is not needed to run Python programs,
to build or to install Python modules, and may be omitted from runtime,
container and desktop images.

%package idle
Summary:    Python IDLE
AutoReq:    no
Requires:   python = %{version}-%{release}
Requires:   python-tkinter = %{version}-%{release}

%description idle
IDLE, Python's integrated development environment.

%package tkinter
Summary:    Python tkinter bindings
AutoReq:    no
Requires:   python = %{version}-%{release}

%description tkinter
The Python tkinter package.  Note that this tree does not build the
_tkinter extension module (there is no Tk package), so the module is
only importable once a Tk-enabled _tkinter is provided.

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
# Install pip from the bundled wheel.  ensurepip itself skips this because the
# build container already has pip in its host site-packages; an explicit
# --ignore-installed install targets the RPM buildroot instead.
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --ignore-installed --force-reinstall \
    %{buildroot}/usr/lib64/python3.14/ensurepip/_bundled/pip-*.whl
if [ -d %{buildroot}/usr/lib/python3.14 ]; then
    mkdir -p %{buildroot}/usr/lib64/python3.14
    cp -a %{buildroot}/usr/lib/python3.14/. %{buildroot}/usr/lib64/python3.14/
    rm -rf %{buildroot}/usr/lib/python3.14
fi
rm -vf %{buildroot}%{_infodir}/dir*
sed -i 's|#!/usr/bin/env python$|#!/usr/bin/env python3|' %{buildroot}/usr/lib64/python3.14/encodings/rot_13.py
ln -s python3.14 %{buildroot}/usr/bin/python
# CPython's "make install" writes bytecode for optimization levels 0, 1 and 2.
# The .opt-1/.opt-2 copies are pure duplicates (~106 MB): -O only strips
# asserts and __debug__ blocks, and Python recompiles them on demand when
# PYTHONOPTIMIZE is set.  Keep only the level-0 .pyc files.
find %{buildroot}/usr/lib64/python3.14 \
    \( -name '*.opt-1.pyc' -o -name '*.opt-2.pyc' \) -delete

%files -f %{_sourcedir}/python.filelist

%files tests -f %{_sourcedir}/python-tests.filelist

%files idle -f %{_sourcedir}/python-idle.filelist

%files tkinter -f %{_sourcedir}/python-tkinter.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.14.7-2
- Drop duplicate .opt-1/.opt-2 bytecode (~106 MB apparent)
- Split the standard library test suite into python-tests
- Split idlelib/idle3 into python-idle and tkinter into python-tkinter
- Generate the filelists from the installed buildroot

* Sat Oct 31 2026 browneye <build@browneye.invalid> 3.14.7
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.14.7
- Sync with LFS r13.1

* Tue May 19 2020 Chris Statzer <chris.statzer@qq.com> 3.7.2-2
- Removed left over tests folder.
