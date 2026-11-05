Name:       x11perf
Version:    1.6.1
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2



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

%files -f %{_sourcedir}/x11perf.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.6.1-1
- Update to x11perf 1.6.1, the latest published x.org release
  (1.6.2 does not exist). Not in the r13.1 book (x.org archive-era
  tool); latest upstream stable 2026-11-05.
