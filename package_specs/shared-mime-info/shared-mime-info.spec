Name:       shared-mime-info
Version:    2.5.1
Release:    4
Summary:    Shared MIME database and update tool
License:    GPL-2.0-or-later
URL:        https://gitlab.freedesktop.org/xdg/shared-mime-info
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

# Rebuild the MIME database whenever a package installs or removes a MIME
# package file.  This replaces the old ad-hoc update-mime-database calls.
%transfiletriggerin -- %{_datadir}/mime
update-mime-database %{_datadir}/mime &>/dev/null || :

%transfiletriggerpostun -- %{_datadir}/mime
update-mime-database %{_datadir}/mime &>/dev/null || :

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 2.5.1-4
- Add file triggers for /usr/share/mime so a package transaction keeps the
  merged MIME database current (issue #35).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.5.1-3
- Replace the TODO summary/description and record the verified license
  (GPL-2.0-or-later): data/freedesktop.org.xml.in (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.5.1-2
- Split lang payload into shared-mime-info-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.5.1
- Sync with 1.10

# let's skip this for now

