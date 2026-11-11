Name:       mkfontscale
Version:    1.2.4
Release:    1
Summary:    Create index of scalable font files
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/mkfontscale
Prefix:     /usr
Source0:    mkfontscale-1.2.4.tar.xz

%description
mkfontscale creates the fonts.scale index for X font directories.

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

%files -f %{_sourcedir}/mkfontscale.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.4-1
- Initial package
