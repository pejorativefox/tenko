Name:       bash
Version:    5.3
Release:    1
Summary:    Bourne Again SHell
License:    GPL3
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

Provides: /bin/bash
Provides: /bin/sh

%description
GNU sh-compatible shell 

%prep
%setup -q

%build
%configure --docdir=/usr/share/doc/bash-%{version} \
           --without-bash-malloc                   \
           --with-installed-readline

%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
pushd %{buildroot}/usr/bin
ln -s bash sh
popd


%files
/usr/bin/sh
/usr/bin/bash
/usr/bin/bashbug
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/include/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/pkgconfig/bash.pc
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/lib64/bash/
/usr/share/doc/bash-%{version}/
/usr/share/info/bash.info.gz
/usr/share/locale/
/usr/share/man/man1/bash.1.gz
/usr/share/man/man1/bashbug.1.gz


%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 5.3
- Sync with LFS r13.1

# let's skip this for now
