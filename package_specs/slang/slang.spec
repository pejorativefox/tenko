Name:       slang
Version:    2.3.3
Release:    2
Summary:    S-Lang interpreter and programmer's library
License:    GPL-2.0-or-later
URL:        https://www.jedsoft.org/slang/
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2
BuildRequires: libpng

%description
S-Lang is an interpreted language designed to be easily embedded into a
program to provide it with a powerful extension language. The S-Lang library
also provides facilities for screen management, keymaps and low-level
terminal I/O.

%prep
%setup -a 0

%build
%configure  --prefix=/usr \
            --sysconfdir=/etc \
            --with-readline=gnu
%make_build -j1


%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/slang.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.3.3-2
- Replace the TODO summary/description and record the verified license
  (GPL-2.0-or-later): src/slang.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.3.3-1
- Sync with the base set

# let's skip this for now

