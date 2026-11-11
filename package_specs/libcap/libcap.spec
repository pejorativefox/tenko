Name:       libcap
Version:    2.78
Release:    3
Summary:    POSIX 1003.1e capabilities
License:    BSD-3-Clause OR GPL-2.0-only
URL:        https://sites.google.com/site/fullycapable/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

Provides: libcap.so.2()(64bit)

%description
POSIX 1003.1e capabilities

%prep
%setup -q 

%build
sed -i '/install -m.*STA/d' libcap/Makefile
%make_build

%install    
rm -rf %{buildroot}
%make_install prefix=/usr
	
%files -f %{_sourcedir}/libcap.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.78-3
- Replace the legacy short licence name with the verified SPDX expression
  (BSD-3-Clause OR GPL-2.0-only): the SPDX header in License (issue #8).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.78-2
- Ship pam_cap.so: with linux-pam-devel present, libcap's Makefile builds
  the PAM module (the base build orders linux-pam before libcap).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.78
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump
