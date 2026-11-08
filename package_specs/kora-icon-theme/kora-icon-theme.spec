Name:       kora-icon-theme
Version:    2.0.6
Release:    2
Summary:    Kora SVG icon theme
License:    GPL-3.0-only
Prefix:     /usr
BuildArch:  noarch
Source0:    kora-%{version}.tar.gz

%description
Kora is an SVG icon theme for GNU/Linux desktops, with blue folder
colours in the main kora theme and grey folders in kora-pgrey.

The theme is scalable and provides HiDPI variants.

%prep
%setup -q -n kora-%{version}

%build

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_datadir}/icons
cp -a --no-preserve=mode kora kora-pgrey %{buildroot}%{_datadir}/icons/
rm -f %{buildroot}%{_datadir}/icons/kora/icon-theme.cache \
      %{buildroot}%{_datadir}/icons/kora/create-new-icon-theme.cache.sh \
      %{buildroot}%{_datadir}/icons/kora-pgrey/icon-theme.cache \
      %{buildroot}%{_datadir}/icons/kora-pgrey/create-new-icon-theme.cache.sh
install -Dpm644 LICENSE %{buildroot}%{_licensedir}/kora-icon-theme/LICENSE
# breeze is not packaged; inherit only hicolor so the theme passes the
# Icon Theme spec's inheritance requirement (issue #35).
for theme in kora kora-pgrey; do
    sed -i 's/^Inherits=.*/Inherits=hicolor/' \
        %{buildroot}%{_datadir}/icons/$theme/index.theme
done

%files -f %{_sourcedir}/kora-icon-theme.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 2.0.6-2
- Inherit only hicolor in both theme index files; breeze is not packaged.
  Drop the %post/%postun icon-cache calls because gtk+ now has a file
  trigger for /usr/share/icons (issue #35).

* Sat Nov 07 2026 tenko <build@tenko.invalid> 2.0.6-1
- New package: latest stable upstream release 2.0.6.
