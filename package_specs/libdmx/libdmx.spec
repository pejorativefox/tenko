Name:       libdmx
Version:    1.1.5
Release:    1
Summary:    X11 Distributed Multihead extension library
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz



%description
TODO

%prep
%setup -q


%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libdmx.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.5-1
- Update to libdmx 1.1.5. Not in the r13.1 book (x.org
  archive-era tool); latest upstream stable 2026-11-05.
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.4-1
- Version bump
