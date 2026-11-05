Name:       shared-mime-info
Version:    2.5.1
Release:    3
Summary:    Shared MIME database and update tool
License:    GPL-2.0-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
%description
The shared-mime-info package contains the core database of common MIME
types, their file extensions and icon names. It also provides the
update-mime-database command used to extend the database and install new
MIME data.

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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.5.1-3
- Replace the TODO summary/description and record the verified license
  (GPL-2.0-or-later): data/freedesktop.org.xml.in (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.5.1-2
- Split lang payload into shared-mime-info-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.5.1
- Sync with BLFS r13.1 (1.10)

# let's skip this for now

