Name:       dejagnu
Version:    1.6.3
Release:    1
Summary:    GNU Test framework
License:    GPL
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
DejaGnu is a framework for testing other programs.

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

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.6.3
- Replace directory globs with a generated static filelist

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Initial RPM

