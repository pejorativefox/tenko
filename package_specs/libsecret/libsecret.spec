Name:       libsecret
Version:    0.21.8.2
Release:    2
Summary:    GObject secret service library
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

BuildRequires: libxslt

%description
The libsecret package contains a GObject based library for accessing the Secret Service API.

%prep
%setup -q

%build
mkdir build-libsecret
pushd build-libsecret
meson setup --prefix=/usr       \
            --buildtype=release \
            -D gtk_doc=false    \
            -D manpage=false    \
            -D vapi=false       \
            ..
ninja
popd

%install    
rm -rf %{buildroot}
pushd build-libsecret
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir

%files
/usr/bin/secret-tool
/usr/include/libsecret-1/libsecret/secret-attributes.h
/usr/include/libsecret-1/libsecret/secret-backend.h
/usr/include/libsecret-1/libsecret/secret-collection.h
/usr/include/libsecret-1/libsecret/secret-enum-types.h
/usr/include/libsecret-1/libsecret/secret-item.h
/usr/include/libsecret-1/libsecret/secret-password.h
/usr/include/libsecret-1/libsecret/secret-paths.h
/usr/include/libsecret-1/libsecret/secret-prompt.h
/usr/include/libsecret-1/libsecret/secret-retrievable.h
/usr/include/libsecret-1/libsecret/secret-schema.h
/usr/include/libsecret-1/libsecret/secret-schemas.h
/usr/include/libsecret-1/libsecret/secret-service.h
/usr/include/libsecret-1/libsecret/secret-types.h
/usr/include/libsecret-1/libsecret/secret-value.h
/usr/include/libsecret-1/libsecret/secret-version.h
/usr/include/libsecret-1/libsecret/secret.h
/usr/lib64/girepository-1.0/Secret-1.typelib
/usr/lib64/libsecret-1.so
/usr/lib64/libsecret-1.so.0
/usr/lib64/libsecret-1.so.0.0.0
/usr/lib64/pkgconfig/libsecret-1.pc
/usr/lib64/pkgconfig/libsecret-unstable.pc
/usr/share/gir-1.0/Secret-1.gir
/usr/share/locale/ab/LC_MESSAGES/libsecret.mo
/usr/share/locale/an/LC_MESSAGES/libsecret.mo
/usr/share/locale/ar/LC_MESSAGES/libsecret.mo
/usr/share/locale/as/LC_MESSAGES/libsecret.mo
/usr/share/locale/be/LC_MESSAGES/libsecret.mo
/usr/share/locale/bg/LC_MESSAGES/libsecret.mo
/usr/share/locale/bs/LC_MESSAGES/libsecret.mo
/usr/share/locale/ca/LC_MESSAGES/libsecret.mo
/usr/share/locale/ca@valencia/LC_MESSAGES/libsecret.mo
/usr/share/locale/ckb/LC_MESSAGES/libsecret.mo
/usr/share/locale/cs/LC_MESSAGES/libsecret.mo
/usr/share/locale/da/LC_MESSAGES/libsecret.mo
/usr/share/locale/de/LC_MESSAGES/libsecret.mo
/usr/share/locale/el/LC_MESSAGES/libsecret.mo
/usr/share/locale/en_GB/LC_MESSAGES/libsecret.mo
/usr/share/locale/eo/LC_MESSAGES/libsecret.mo
/usr/share/locale/es/LC_MESSAGES/libsecret.mo
/usr/share/locale/eu/LC_MESSAGES/libsecret.mo
/usr/share/locale/fa/LC_MESSAGES/libsecret.mo
/usr/share/locale/fi/LC_MESSAGES/libsecret.mo
/usr/share/locale/fr/LC_MESSAGES/libsecret.mo
/usr/share/locale/fur/LC_MESSAGES/libsecret.mo
/usr/share/locale/gl/LC_MESSAGES/libsecret.mo
/usr/share/locale/he/LC_MESSAGES/libsecret.mo
/usr/share/locale/hi/LC_MESSAGES/libsecret.mo
/usr/share/locale/hr/LC_MESSAGES/libsecret.mo
/usr/share/locale/hu/LC_MESSAGES/libsecret.mo
/usr/share/locale/id/LC_MESSAGES/libsecret.mo
/usr/share/locale/ie/LC_MESSAGES/libsecret.mo
/usr/share/locale/it/LC_MESSAGES/libsecret.mo
/usr/share/locale/ja/LC_MESSAGES/libsecret.mo
/usr/share/locale/ka/LC_MESSAGES/libsecret.mo
/usr/share/locale/kab/LC_MESSAGES/libsecret.mo
/usr/share/locale/kk/LC_MESSAGES/libsecret.mo
/usr/share/locale/ko/LC_MESSAGES/libsecret.mo
/usr/share/locale/kw/LC_MESSAGES/libsecret.mo
/usr/share/locale/lo/LC_MESSAGES/libsecret.mo
/usr/share/locale/lt/LC_MESSAGES/libsecret.mo
/usr/share/locale/lv/LC_MESSAGES/libsecret.mo
/usr/share/locale/ml/LC_MESSAGES/libsecret.mo
/usr/share/locale/ms/LC_MESSAGES/libsecret.mo
/usr/share/locale/nb/LC_MESSAGES/libsecret.mo
/usr/share/locale/ne/LC_MESSAGES/libsecret.mo
/usr/share/locale/nl/LC_MESSAGES/libsecret.mo
/usr/share/locale/oc/LC_MESSAGES/libsecret.mo
/usr/share/locale/pa/LC_MESSAGES/libsecret.mo
/usr/share/locale/pl/LC_MESSAGES/libsecret.mo
/usr/share/locale/pt/LC_MESSAGES/libsecret.mo
/usr/share/locale/pt_BR/LC_MESSAGES/libsecret.mo
/usr/share/locale/ro/LC_MESSAGES/libsecret.mo
/usr/share/locale/ru/LC_MESSAGES/libsecret.mo
/usr/share/locale/sk/LC_MESSAGES/libsecret.mo
/usr/share/locale/sl/LC_MESSAGES/libsecret.mo
/usr/share/locale/sr/LC_MESSAGES/libsecret.mo
/usr/share/locale/sr@latin/LC_MESSAGES/libsecret.mo
/usr/share/locale/sv/LC_MESSAGES/libsecret.mo
/usr/share/locale/ta/LC_MESSAGES/libsecret.mo
/usr/share/locale/tg/LC_MESSAGES/libsecret.mo
/usr/share/locale/th/LC_MESSAGES/libsecret.mo
/usr/share/locale/tr/LC_MESSAGES/libsecret.mo
/usr/share/locale/ug/LC_MESSAGES/libsecret.mo
/usr/share/locale/uk/LC_MESSAGES/libsecret.mo
/usr/share/locale/uz/LC_MESSAGES/libsecret.mo
/usr/share/locale/vi/LC_MESSAGES/libsecret.mo
/usr/share/locale/zh_CN/LC_MESSAGES/libsecret.mo
/usr/share/locale/zh_HK/LC_MESSAGES/libsecret.mo
/usr/share/locale/zh_TW/LC_MESSAGES/libsecret.mo

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.21.8.2-2
- Record the verified license (LGPL-2.1-or-later): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.21.8.2-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.21.0-1
- Version bump

