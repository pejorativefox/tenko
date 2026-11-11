Name:       encodings
Version:    1.1.0
Release:    2
Summary:    X.org font encodings
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/font/encodings
Prefix:     /usr
Source0:    encodings-1.1.0.tar.xz
BuildRequires: util-macros
BuildRequires: mkfontscale

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
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.1.0-2
- Rebuild: the published metadata still described the earlier
  build of this NEVRA, so dnf rejected the server file on a
  size/checksum mismatch.  Same content, new release.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.1.0
- Sync with encodings 1.1.0
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.1.0
- Sync with encodings 1.1.0
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.0-1
- Initial package
