Name:       libisofs
Version:    1.5.8.pl02
Release:    1
Summary:    Library to create ISO-9660 filesystems with RockRidge and Joliet
License:    GPL-2.0-or-later
URL:        https://dev.lovelyhq.com/libburnia/web/wiki
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
libisofs is a library to create an ISO-9660 filesystem with extensions like
RockRidge or Joliet.  It is used by libisoburn (xorriso), which the Tenko
installer uses to build and expand installation ISOs.

%prep
# Upstream ships 1.5.8.pl02 in a directory named after the 1.5.8 base.
%setup -q -n %{name}-1.5.8

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir* %{buildroot}%{_libdir}/libisofs.la

%files -f %{_sourcedir}/libisofs.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.5.8.pl02-1
- Initial package
- Build with --disable-static as the base build specifies; drop the libtool archive
