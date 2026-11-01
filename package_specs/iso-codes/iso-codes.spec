Name:       iso-codes
Version:    4.20.1
Release:    2
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    iso-codes-v4.20.1.tar.gz

%description
TODO

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
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.1-2
- Split lang payload into iso-codes-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.1
- Sync with BLFS r13.1 (4.3)

# let's skip this for now

