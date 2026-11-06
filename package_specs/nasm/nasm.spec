Name:       nasm
Version:    3.02
Release:    2
Summary:    Netwide Assembler for x86 and x86-64
License:    BSD-2-Clause
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz


%description
NASM is the Netwide Assembler, a portable assembler for x86 and x86-64. It
supports many output formats, including ELF, Mach-O, COFF and raw binary.

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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.02-2
- Replace the TODO summary/description and record the verified license
  (BSD-2-Clause): LICENSE (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.02-1
- Sync with the base set

# let's skip this for now

