Name:       font-bh-ttf
Version:    1.0.4
Release:    1
Summary:    Bigelow & Holmes TrueType fonts
License:    MIT
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
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.0.4-1
- Initial package (BLFS r13.1)
