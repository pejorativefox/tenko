Name:       libtasn1
Version:    4.21.0
Release:    1
Summary:    Library for ASN.1 and DER manipulation
License:    GPL-3.0-or-later
URL:        https://www.gnu.org/software/libtasn1/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
libtasn1 is a highly portable C library that encodes and decodes DER/BER
data following an ASN.1 schema.  It is used by p11-kit and GnuTLS.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir

%files -f %{_sourcedir}/libtasn1.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.21.0
- Update to 4.21.0 (BLFS r13.1)
- Replace the directory listing with a generated static filelist
