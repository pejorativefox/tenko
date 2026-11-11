Name:       imlib2
Version:    1.12.7
Release:    1
Summary:    imlib2 is a general image loading and rendering library
License:    imlib2
URL:        https://git.enlightenment.org/old/legacy-imlib2
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: cairo
BuildRequires: freetype
BuildRequires: gdk-pixbuf
BuildRequires: libjpeg-turbo
BuildRequires: libpng
BuildRequires: librsvg
BuildRequires: libx11
BuildRequires: libxcb
BuildRequires: libxext

%description
imlib2 is a general image loading and rendering library

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/imlib2.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.12.7-1
- Sync with the base set

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 1.12.0
- Initial RPM

