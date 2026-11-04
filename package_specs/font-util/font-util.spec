Name:       font-util
Version:    1.4.2
Release:    2
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
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.4.2-2
- Rebuild: the published metadata still described the earlier
  build of this NEVRA, so dnf rejected the server file on a
  size/checksum mismatch.  Same content, new release.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.4.2
- Sync with BLFS r13.1 (font-util 1.4.2)
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.4.2
- Sync with BLFS r13.1 (font-util 1.4.2)
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.4.2-1
- Initial package (BLFS r13.1)
