Name:       lcms2
Version:    2.20
Release:    1
Summary:    Little CMS colour management engine
License:    MIT
URL:        https://www.littlecms.com/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: libjpeg-turbo

%description
Little CMS is a small, fast colour management engine implementing ICC
profiles (version 2 and 4).  It converts colours between device and
working spaces and is used by kitty for colour-managed rendering.  The
package includes the transicc, linkicc, psicc and jpgicc utilities.

%prep
%setup -q

%build
# No libtiff package in Tenko, so tificc is not built.
%configure --disable-static --with-jpeg --without-tiff
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -f %{buildroot}%{_libdir}/liblcms2.la
# tificc is not built (no libtiff), but its man page is installed anyway.
rm -f %{buildroot}%{_mandir}/man1/tificc.1

%check
make check

%files -f %{_sourcedir}/lcms2.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 2.20-1
- New package, not in the base set: latest upstream stable release (2.20,
  checked 2026-11-14).  Needed by kitty (colour management).
