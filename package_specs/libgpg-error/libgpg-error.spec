Name:       libgpg-error
Version:    1.61
Release:    1
Summary:    Library that defines common error values for GnuPG components
License:    LGPL
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

%description
libgpg-error is a small library that defines common error values for all
GnuPG components.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
ln -sfv gpgrt-config %{buildroot}/usr/bin/gpg-error-config

%files -f %{_sourcedir}/libgpg-error.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.61-1
- Update to the BLFS r13.1 version (1.61, was 1.47) for the E1
  dnf/libdnf dependency chain.
- Use a generated static filelist.
