Name:       libburn
Version:    1.5.8
Release:    1
Summary:    Library for writing preformatted data onto optical media
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
libburn is a library for writing preformatted data onto optical media: CD,
DVD and BD (Blu-Ray).  It provides cdrskin and is the media-writing backend
for libisoburn (xorriso), which the Tenko installer uses to write ISOs.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir* %{buildroot}%{_libdir}/libburn.la

%files -f %{_sourcedir}/libburn.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.5.8-1
- Initial package
- Build with --disable-static as the base build specifies; drop the libtool archive
