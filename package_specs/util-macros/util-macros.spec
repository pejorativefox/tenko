Name:       util-macros
Version:    1.20.2
Release:    1
Summary:    X.org autotools macros
License:    MIT
Prefix:     /usr
Source0:    util-macros-1.20.2.tar.xz

%description
util-macros provides the autoconf macros used by X.org packages.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/util-macros.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.20.2-1
- Initial package
