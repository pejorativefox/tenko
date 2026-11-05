Name:       dejagnu
Version:    1.6.3
Release:    3
Summary:    GNU Test framework
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
DejaGnu is a framework for testing other programs.

%package doc
Summary:    dejagnu documentation
License:    GFDL-1.3-no-invariants-or-later
Requires:   dejagnu = %{version}-%{release}

%description doc
Documentation for dejagnu.

%prep
%setup

%build
mkdir build
pushd build
../configure --prefix=/usr --libdir=%{_libdir}
makeinfo --html --no-split -o doc/dejagnu.html ../doc/dejagnu.texi
makeinfo --plaintext       -o doc/dejagnu.txt  ../doc/dejagnu.texi
popd

%install
rm -rf %{buildroot}
pushd build
install -v -dm755  %{buildroot}/usr/share/doc/dejagnu-1.6.3
install -v -m644   doc/dejagnu.{html,txt} %{buildroot}/usr/share/doc/dejagnu-1.6.3
%make_install
rm %{buildroot}/usr/share/info/dir
popd

%files -f %{_sourcedir}/dejagnu.filelist
%files doc -f %{_sourcedir}/dejagnu-doc.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.6.3-3
- Replace the legacy short licence name with the verified SPDX expressions
  (GPL-3.0-or-later for the code, GFDL-1.3-no-invariants-or-later for the
  docs): COPYING, runtest.exp and doc/dejagnu.texi (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.6.3-2
- Split doc payload into dejagnu-doc (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.6.3
- Replace directory globs with a generated static filelist

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Initial RPM

