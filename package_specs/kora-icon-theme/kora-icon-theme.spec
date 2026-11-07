Name:       kora-icon-theme
Version:    2.0.6
Release:    1
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

%post
for theme in kora kora-pgrey; do
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -q -t -f %{_datadir}/icons/$theme || :
    fi
done

%postun
for theme in kora kora-pgrey; do
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -q -t -f %{_datadir}/icons/$theme || :
    fi
done

%files -f %{_sourcedir}/kora-icon-theme.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 2.0.6-1
- New package: latest stable upstream release 2.0.6.
