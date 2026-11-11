Name:       bash
Version:    5.3
Release:    4
Summary:    Bourne Again SHell
License:    GPL-3.0-or-later
URL:        https://www.gnu.org/software/bash/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

Provides: /bin/bash
Provides: /bin/sh

%description
GNU sh-compatible shell 

%package lang
Summary:    bash translations
Requires:   bash = %{version}-%{release}

%description lang
Translations for bash.

%package doc
Summary:    bash documentation
Requires:   bash = %{version}-%{release}

%description doc
Documentation for bash.

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

%files -f %{_sourcedir}/bash.filelist
%files lang -f %{_sourcedir}/bash-lang.filelist
%files doc -f %{_sourcedir}/bash-doc.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.3-4
- Record the verified license (GPL-3.0-or-later): README (version 3 or later) and braces.c (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.3-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 5.3-2
- Split lang, doc, devel payload into bash-lang, bash-doc, bash-devel (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 5.3
- Sync with the base set

# let's skip this for now
