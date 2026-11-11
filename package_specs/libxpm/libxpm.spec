Name:       libxpm
Version:    3.5.20
Release:    1
Summary:    XPM file format
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxpm
Prefix:     /usr
Source0:    libXpm-3.5.20.tar.xz

%description
X Pixmap (XPM) image file format library.

%prep
%setup -q -n libXpm-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxpm.filelist
%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.5.20
- Sync with libxpm 3.5.20
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 3.5.16
- Version bump
