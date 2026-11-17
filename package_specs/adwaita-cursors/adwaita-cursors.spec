Name:       adwaita-cursors
Version:    1.2
Release:    1
Summary:    Adwaita cursor theme in intermediate sizes with extra aliases
License:    GPL-3.0-only OR CC-BY-SA-3.0
URL:        https://github.com/manu-mannattil/adwaita-cursors
Prefix:     /usr
BuildArch:  noarch
Source0:    adwaita-cursors-%{version}.tar.gz
# The release tarball ships the PNGs rendered from adwaita.svg, so the
# Inkscape step is not part of a distribution build.
Patch0:     adwaita-cursors-%{version}-prebuilt-pngs.patch
# grab (hand1) is the open-hand cursor; left_ptr is the plain arrow.
# Matches upstream ffec17b0, committed after the 1.2 release.
Patch1:     adwaita-cursors-%{version}-openhand-alias.patch

BuildRequires: xcursorgen

%description
GNOME's Adwaita cursor theme rendered at 24, 30, 36, 42, 48, 54, 60, 66,
72, 78, 84, 90 and 96 pixels, for displays whose fractional scaling makes
the five sizes in adwaita-icon-theme too coarse.  It also carries the
cursor aliases some Qt 5 applications expect (openhand, closedhand).

An "Adwaita-red" variant, generated from the same artwork with the
colorize.py helper, is installed as well.

%prep
%setup -q -n adwaita-cursors
%patch -P 0 -p1
%patch -P 1 -p1

%build
make

%install
rm -rf %{buildroot}
# /usr/share/icons/Adwaita/index.theme belongs to the icon theme and stays
# in adwaita-icon-theme, which requires this package for the cursors.
install -d %{buildroot}%{_datadir}/icons/Adwaita/cursors
cp -a Adwaita/cursors/. %{buildroot}%{_datadir}/icons/Adwaita/cursors/
install -Dpm644 Adwaita/cursor.theme \
    %{buildroot}%{_datadir}/icons/Adwaita/cursor.theme
cp -a Adwaita-red %{buildroot}%{_datadir}/icons/
install -Dpm644 LICENSE %{buildroot}%{_licensedir}/adwaita-cursors/LICENSE

%files -f %{_sourcedir}/adwaita-cursors.filelist

%changelog
* Tue Nov 17 2026 tenko <build@tenko.invalid> 1.2-1
- New package, not in the base set: latest upstream stable release
  (1.2, checked 2026-11-17).  It provides the Adwaita cursor theme at
  thirteen sizes plus the Adwaita-red variant; adwaita-icon-theme keeps
  the icon payload and requires this package for the cursors.  The
  release tarball carries pre-rendered PNGs, so the build needs no
  Inkscape, and the openhand alias matches the fix upstream made after
  1.2.
