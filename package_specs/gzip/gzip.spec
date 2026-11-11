Name:       gzip
Version:    1.15
Release:    2
Summary:    GNU data compression program
License:    GPL-3.0-or-later
URL:        https://www.gnu.org/software/gzip/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: less

%description
Gzip is a popular data compression program originally written by Jean-loup Gailly for the GNU project. 

%prep
%setup -q

%build

%configure 
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/gzip.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.15-2
- Record the verified license (GPL-3.0-or-later): gzip.c (issue #8).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 1.15-1
- Update to 1.15 (current upstream version).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.14
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.12-1
- Version bump
