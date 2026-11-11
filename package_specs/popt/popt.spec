Name:       popt
Version:    1.19
Release:    2
Summary:    popt command line option parsing library.
License:    MIT
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
popt command line option parsing library.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/popt.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.19-2
- Record the verified license (MIT): COPYING (issue #8).

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.19-1
- Version bump
