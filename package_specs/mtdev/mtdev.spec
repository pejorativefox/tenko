Name:       mtdev
Version:    1.1.7
Release:    1
Summary:    Multitouch protocol translation library
License:    MIT
Prefix:     /usr
Source0:    mtdev-1.1.7.tar.bz2

%description
mtdev converts kernel multitouch events to the MT protocol.

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

%files -f %{_sourcedir}/mtdev.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.7-1
- Initial package (BLFS r13.1)
