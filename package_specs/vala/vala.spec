Name:       vala
Version:    0.56.19
Release:    2
Summary:    Vala programming language.
License:    LGPL-2.1-or-later AND (GPL-3.0-or-later WITH Bison-exception-2.2)
URL:        https://vala.dev/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: gobject-introspection

%description
Vala is a new programming language that aims to bring modern programming language features to GNOME developers without imposing any additional runtime requirements and without using a different ABI compared to applications and libraries written in C. 

%prep
%setup

%build
%configure --disable-valadoc
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/vala.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.56.19-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later AND (GPL-3.0-or-later WITH Bison-exception-2.2)): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.56.19-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.40.8
- Initial RPM

