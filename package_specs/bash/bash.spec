Name:       bash
Version:    5.3
Release:    2
Summary:    Bourne Again SHell
License:    GPL3
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

%package devel
Summary:    bash development files
Requires:   bash = %{version}-%{release}

%description devel
Development files for bash.

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
%files devel -f %{_sourcedir}/bash-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 5.3-2
- Split lang, doc, devel payload into bash-lang, bash-doc, bash-devel (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 5.3
- Sync with LFS r13.1

# let's skip this for now
