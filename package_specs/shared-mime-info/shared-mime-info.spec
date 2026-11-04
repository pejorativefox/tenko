Name:       shared-mime-info
Version:    2.5.1
Release:    2
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
%description
TODO

%package lang
Summary:    shared-mime-info translations
Requires:   shared-mime-info = %{version}-%{release}

%description lang
Translations for shared-mime-info.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                  \
      --prefix=/usr             \
      --buildtype=release       \
      -D update-mimedb=true     \
      -D build-tests=false      \
      -D build-spec=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/shared-mime-info.filelist
%files lang -f %{_sourcedir}/shared-mime-info-lang.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.5.1-2
- Split lang payload into shared-mime-info-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.5.1
- Sync with BLFS r13.1 (1.10)

# let's skip this for now

