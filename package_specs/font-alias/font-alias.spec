Name:       font-alias
Version:    1.0.6
Release:    2
Summary:    X.org font aliases
License:    MIT
Prefix:     /usr
Source0:    font-alias-1.0.6.tar.xz

%description
font-alias provides the X core font alias files.

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

%files -f %{_sourcedir}/font-alias.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.0.6-2
- Rebuild: the published metadata still described the earlier
  build of this NEVRA, so dnf rejected the server file on a
  size/checksum mismatch.  Same content, new release.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.0.6
- Sync with font-alias 1.0.6
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.0.6
- Sync with font-alias 1.0.6
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.0.6-1
- Initial package
