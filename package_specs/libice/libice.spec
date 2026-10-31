Name:       libice
Version:    1.1.2
Release:    1
Summary:    Inter-Client Exchange Library.
License:    GPL3
Prefix:     /usr
Source0:    libICE-1.1.2.tar.xz

%description
Inter-Client Exchange Library.

%prep
%setup -q -n libICE-%{version}

%build
%configure ICE_LIBS=-lpthread
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.1.2
- Sync with BLFS r13.1 (1.1.1)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.1-1
- Version bump
