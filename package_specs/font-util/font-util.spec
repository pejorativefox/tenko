Name:       font-util
Version:    1.4.2
Release:    1
Summary:    X.org font utility macros
License:    MIT
Prefix:     /usr
Source0:    font-util-1.4.2.tar.xz

%description
font-util provides the autoconf macros and utilities used by X font packages.

%prep
%setup -q

%build
%configure --with-fontrootdir=/usr/share/fonts
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/font-util.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.4.2-1
- Initial package (BLFS r13.1)
