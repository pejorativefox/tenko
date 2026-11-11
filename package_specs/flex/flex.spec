Name:       flex
Version:    2.6.4
Release:    2
Summary:    Fast lexical analyzer generator
License:    BSD-3-Clause
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
flex is a tool for generating scanners: programs which recognize lexical
patterns in text. It takes a description of the tokens to recognize and
produces C source code for a lexical analyzer.

%prep
%setup -q -a0

%build
sed -i "/math.h/a #include <malloc.h>" src/flexdef.h
%configure --docdir=/usr/share/doc/flex-2.6.4
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/flex.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.6.4-2
- Replace the TODO summary/description and record the verified license
  (BSD-3-Clause): COPYING (issue #8).

# let's skip this for now
