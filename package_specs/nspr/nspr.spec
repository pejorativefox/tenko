Name:       nspr
Version:    4.40
Release:    2
Summary:    Netscape Portable Runtime
License:    MPL-2.0
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Netscape Portable Runtime (NSPR) provides a platform-neutral API for system level and libc like functions. 

%prep
%setup -q

%build
pushd nspr
sed -ri '/^RELEASE/s/^/#/' pr/src/misc/Makefile.in 
sed -i 's#$(LIBRARY) ##'   config/rules.mk         

%configure --enable-64bit --with-mozilla --with-pthreads
%make_build
popd

%install    
rm -rf %{buildroot}
pushd nspr
%make_install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/nspr.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.40-2
- Record the verified license (MPL-2.0): LICENSE (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 4.40-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 4.35-1
- Version bump
