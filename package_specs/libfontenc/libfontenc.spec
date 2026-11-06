Name:       libfontenc
Version:    1.1.9
Release:    1
Summary:    X.org font encoding library
License:    MIT
Prefix:     /usr
Source0:    libfontenc-1.1.9.tar.xz

%description
libfontenc decodes the various font encodings used by X.

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

%files -f %{_sourcedir}/libfontenc.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.9-1
- Initial package
