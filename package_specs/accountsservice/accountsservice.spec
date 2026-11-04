Name:       accountsservice
Version:    26.27.3
Release:    2
Summary:    D-Bus service for querying and manipulating user accounts
License:    GPL-3.0-or-later
Source0:    accountsservice-26.27.3.tar.bz2
Source1:    40-adm.rules
Prefix:     /usr

BuildRequires: meson, ninja, gettext
BuildRequires: json-c, polkit, glib, systemd, gobject-introspection

Requires: json-c
Requires: polkit
# logind is used to track sessions/seat state.
Requires: systemd

%description
AccountsService provides a set of D-Bus interfaces for querying and
manipulating user account information, backed by useradd/usermod/userdel.
LightDM's greeter uses it to list local users and their icons.

%package lang
Summary:    accountsservice translations
Requires:   accountsservice = %{version}-%{release}

%description lang
Translations for accountsservice.

%package devel
Summary:    accountsservice development files
Requires:   %{name}-gir = %{version}-%{release}
Requires:   accountsservice = %{version}-%{release}

%description devel
Headers, pkg-config file and GObject introspection data for
libaccountsservice.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. \
    --prefix=%{_prefix} \
    --buildtype=release \
    --libdir=%{_libdir} \
    -D admin_group=adm \
    -D vapi=false \
    -D docbook=false \
    -D gtk_doc=false
ninja
popd

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install
install -Dpm0644 %{SOURCE1} %{buildroot}/etc/polkit-1/rules.d/40-adm.rules
# accounts-daemon.service lists this path under ReadOnlyPaths= without the
# '-' prefix, so it must exist or the unit fails to start.  Upstream installs
# the interfaces into /usr/share/dbus-1/interfaces instead.
install -dm0755 %{buildroot}%{_datadir}/accountsservice/interfaces


%package gir
Summary:    GObject Introspection data for accountsservice
License:    GPL-3.0-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for accountsservice.  They were installed by the
-devel package, which is where upstream's build puts them; the .gir
XML needed for building stays there.

%files -f %{_sourcedir}/accountsservice.filelist

%files lang -f %{_sourcedir}/accountsservice-lang.filelist

%files devel -f %{_sourcedir}/accountsservice-devel.filelist
%files gir -f %{_sourcedir}/accountsservice-gir.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 26.27.3-2
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Mon Nov 02 2026 browneye <build@browneye.invalid> 26.27.3-1
- Initial package (BLFS r13.1 AccountsService 26.27.3) for the LightDM
  greeter user list
- No Vala bindings (vala not packaged) and no API/dbus docs
- Ship the BLFS adm-group polkit rule
