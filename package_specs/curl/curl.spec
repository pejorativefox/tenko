Name:       curl
Version:    8.23.0
Release:    1
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
%configure --disable-static --with-openssl --with-ca-path=/etc/ssl/certs
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/curl.filelist
%files doc -f %{_sourcedir}/curl-doc.filelist
%files devel -f %{_sourcedir}/curl-devel.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 8.23.0-1
- Update to 8.23.0 (BLFS r13.1 trunk).
- Enable Public Suffix List support: libpsl 0.23.3 (with libidn2 2.3.8 and
  libunistring 1.5) is now packaged, so drop --without-libpsl.  BLFS notes
  that building without libpsl has severe security implications for cookie
  and HSTS domain scoping.
* Sun Nov 01 2026 browneye <build@browneye.invalid> 8.22.0-2
- Split doc, devel payload into curl-doc, curl-devel (size audit)

# let's skip this for now
