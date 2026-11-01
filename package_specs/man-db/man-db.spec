Name:       man-db
Version:    2.13.1
Release:    2
Summary:    Man page utilities
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The Man-DB package contains programs for finding and viewing man pages.

%package lang
Summary:    man-db translations
Requires:   man-db = %{version}-%{release}

%description lang
Translations for man-db.

%prep
%setup -q

%build

%configure  --docdir=/usr/share/doc/man-db-%{version} \
            --sysconfdir=/etc                    \
            --disable-setuid                     \
            --enable-cache-owner=bin             \
            --with-browser=/usr/bin/lynx         \
            --with-vgrind=/usr/bin/vgrind        \
            --with-grap=/usr/bin/grap            \
            --with-systemdtmpfilesdir=           \
            --with-systemdsystemunitdir=
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/man-db.filelist
%files lang -f %{_sourcedir}/man-db-lang.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.13.1-2
- Split lang payload into man-db-lang (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.13.1
- Sync with LFS r13.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2.11.12-1
- Version bump
