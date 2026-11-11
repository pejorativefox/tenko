Name:       libndp
Version:    1.9
Release:    2
Summary:    Library for the IPv6 Neighbor Discovery Protocol
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz


%description
libndp provides a wrapper for the IPv6 Neighbor Discovery Protocol. It also
includes ndptool, a utility for sending and receiving NDP messages.

%prep
%setup

%build
%configure  --sysconfdir=/etc    \
            --localstatedir=/var \
            --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libndp.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.9-2
- Replace the TODO summary/description and record the verified license
  (LGPL-2.1-or-later): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.9-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.7-1
- Version bump

