Name:       yasm
Version:    1.3.0
Release:    2
Summary:    Complete rewrite of the NASM assembler
License:    BSD-2-Clause AND BSD-3-Clause AND (Artistic-1.0-Perl OR GPL-2.0-or-later OR LGPL-2.0-or-later)
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
Yasm is a complete rewrite of the NASM assembler. It supports the x86
and AMD64 instruction sets, accepts NASM and GAS assembler syntaxes and
outputs binary, ELF32 and ELF64 object formats.

%prep
%setup -q -n %{name}-%{version}
sed -e 's/def __cplusplus/ defined(__cplusplus) || __STDC_VERSION__ >= 202311L/' \
    -i libyasm/bitvect.h
sed -i 's#) ytasm.*#)#' Makefile.in

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/yasm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.3.0-2
- Replace the legacy short licence name with the verified SPDX expression
  (BSD-2-Clause AND BSD-3-Clause AND (Artistic-1.0-Perl OR GPL-2.0-or-later OR LGPL-2.0-or-later)): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.3.0-1
- Rebuild from the BLFS r13.1 page
  (general/prog/yasm.xml, 1.3.0).
- Apply the book's gcc-15 C++ guard fix to libyasm/bitvect.h.
- Refresh %files from the build (no -devel split).
