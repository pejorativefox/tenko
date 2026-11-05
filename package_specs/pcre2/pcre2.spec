Name:       pcre2
Version:    10.49
Release:    2
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

%description
TODO

%package doc
Summary:    pcre2 documentation
Requires:   pcre2 = %{version}-%{release}

%description doc
Documentation for pcre2.

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

%files -f %{_sourcedir}/pcre2.filelist
%files doc -f %{_sourcedir}/pcre2-doc.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 10.49-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 10.49-1
- Update to 10.49 (current LFS/BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 10.48-2
- Split doc, devel payload into pcre2-doc, pcre2-devel (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 10.47
- Sync with LFS r13.1

# let's skip this for now

