Name:       nasm
Version:    3.02
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz


%description
TODO

%prep
%setup -a 0

%build
%configure  
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/nasm
/usr/bin/ndisasm
/usr/share/man/man1/nasm.1.gz
/usr/share/man/man1/ndisasm.1.gz

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.02-1
- Sync with BLFS r13.1

# let's skip this for now

