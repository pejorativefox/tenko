Name:       curl
Version:    8.22.0
Release:    2
Summary:    TODO
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
TODO

%package doc
Summary:    curl documentation
Requires:   curl = %{version}-%{release}

%description doc
Documentation for curl.

%package devel
Summary:    curl development files
Requires:   curl = %{version}-%{release}

%description devel
Development files for curl.

%prep
%setup -q -a0

%build
%configure --disable-static --with-openssl --with-ca-path=/etc/ssl/certs --without-libpsl
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/curl.filelist
%files doc -f %{_sourcedir}/curl-doc.filelist
%files devel -f %{_sourcedir}/curl-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 8.22.0-2
- Split doc, devel payload into curl-doc, curl-devel (size audit)

# let's skip this for now
