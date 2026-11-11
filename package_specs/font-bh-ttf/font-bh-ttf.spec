Name:       font-bh-ttf
Version:    1.0.4
Release:    2
Summary:    Bigelow & Holmes TrueType fonts
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/font/bh-ttf
Prefix:     /usr
Source0:    font-bh-ttf-1.0.4.tar.xz

%description
The Bigelow & Holmes Luxi TrueType fonts (Bitstream Vera family).

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

%files -f %{_sourcedir}/font-bh-ttf.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.0.4-2
- Rebuild: the published metadata still described the earlier
  build of this NEVRA, so dnf rejected the server file on a
  size/checksum mismatch.  Same content, new release.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.0.4
- Sync with font-bh-ttf 1.0.4
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.0.4
- Sync with font-bh-ttf 1.0.4
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.0.4-1
- Initial package
