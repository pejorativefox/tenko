Name:       sed
Version:    4.10
Release:    1
Summary:    The sed stream editor
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
sed (stream editor) is a non-interactive command-line text editor. 

%prep
%setup -q

%build
%configure --without-selinux
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*


%files
/usr/bin/sed
/usr/share/info/sed.info.gz
/usr/share/locale/
/usr/share/man/man1/sed.1.gz

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.10
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump
