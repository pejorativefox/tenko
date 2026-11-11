Name:       nasm
Version:    3.02
Release:    2
Summary:    Netwide Assembler for x86 and x86-64
License:    BSD-2-Clause
URL:        https://www.nasm.us/
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

%files -f %{_sourcedir}/nasm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.02-2
- Replace the TODO summary/description and record the verified license
  (BSD-2-Clause): LICENSE (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.02-1
- Sync with the base set

# let's skip this for now

