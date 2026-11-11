Name:       intltool
Version:    0.51.0
Release:    2
Summary:    gettext file processor
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
intltool is a set of tools to centralize translation of many different file formats using GNU gettext-compatible PO files.

%prep
%setup -q -a0

%build
sed -i 's:\\\${:\\\$\\{:' intltool-update.in
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/intltool.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.51.0-2
- Record the verified license (GPL-2.0-or-later): COPYING and intltoolize.in (issue #8).

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 0.51.0-1
- Version bump
