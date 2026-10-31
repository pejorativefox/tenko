Name:       libxres
Version:    1.2.3
Release:    1
Summary:    X-Resource extension client library
License:    GPL3
Prefix:     /usr
Source0:    libXres-1.2.3.tar.xz

%description
X-Resource extension client library

%prep
%setup -q -n libXres-%{version}


%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.2.3
- Sync with BLFS r13.1 (1.2.2)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.2-1
- Version bump
