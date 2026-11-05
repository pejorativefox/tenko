Name:       iso-codes
Version:    4.20.1
Release:    3
Summary:    ISO standards code lists and translations
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    iso-codes-v4.20.1.tar.gz

%description
iso-codes provides lists of various ISO standards, such as country,
language, language script and currency names, in one place rather than
repeated in many programs throughout the system. The data is available
through gettext domains so programs can reuse the translations.

%package lang
Summary:    iso-codes translations
Requires:   iso-codes = %{version}-%{release}

%description lang
Translations for iso-codes.

%prep
%setup -q -n iso-codes-v%{version}

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/iso-codes.filelist
%files lang -f %{_sourcedir}/iso-codes-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.1-3
- Replace the TODO summary/description and record the verified license
  (LGPL-2.1-or-later): REUSE.toml (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.1-2
- Split lang payload into iso-codes-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.1
- Sync with BLFS r13.1 (4.3)

# let's skip this for now

