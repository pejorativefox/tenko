Name:       libsm
Version:    1.2.6
Release:    1
Summary:    X Session Management Library
License:    GPL3
Prefix:     /usr
Source0:    libSM-1.2.6.tar.xz

BuildRequires: libice

%description
X Session Management Library

%prep
%setup -q -n libSM-%{version}

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
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.2.6
- Sync with BLFS r13.1 (1.2.4)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.4-1
- Version bump
