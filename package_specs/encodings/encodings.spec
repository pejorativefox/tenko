Name:       encodings
Version:    1.1.0
Release:    1
Summary:    X.org font encodings
License:    MIT
Prefix:     /usr
Source0:    encodings-1.1.0.tar.xz

%description
The X.org font encoding data.

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

%files -f %{_sourcedir}/encodings.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.1.0
- Sync with BLFS r13.1 (encodings 1.1.0)
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.1.0
- Sync with BLFS r13.1 (encodings 1.1.0)
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.0-1
- Initial package (BLFS r13.1)
