Name:       lightdm
Version:    1.33.1
Release:    4
Summary:    Lightweight cross-desktop display manager
License:    GPL-3.0-or-later
Source0:    lightdm-1.33.1.tar.gz
Source1:    lightdm.service
Source2:    50-lightdm.preset
Prefix:     /usr

# Upstream still uses intltool for the polkit policy; the rest is autotools.
BuildRequires: autoconf, automake, libtool, gettext, intltool
BuildRequires: linux-pam, libgcrypt, libxklavier
BuildRequires: glib, gtk+, libxcb, libxdmcp
BuildRequires: gobject-introspection

# The greeter is packaged separately but is what lightdm starts.
Requires:      xorg-server
Requires:      lightdm-gtk-greeter
Requires(pre): shadow

%description
LightDM is a lightweight, cross-desktop display manager.  It runs the X
server and presents a graphical login screen from an external greeter
(lightdm-gtk-greeter in Tenko).

%package lang
Summary:    lightdm translations
Requires:   lightdm = %{version}-%{release}

%description lang
Translations for lightdm.

%prep
%setup -q
# The yelp help build needs yelp-tools and itstool, which we do not ship; the
# manual is reachable through the LightDM site instead.
sed -i '/YELP_HELP/d' configure.ac help/Makefile.am
# GTK_DOC_CHECK would require gtk-doc/gtkdocize to generate gtk-doc.make; we
# do not ship API documentation, so drop the macro entirely.
sed -i '/GTK_DOC_CHECK/d' configure.ac
# doc/Makefile.am unconditionally includes gtk-doc.make, which only gtkdocize
# would create; an empty file keeps automake happy without gtk-doc installed.
: > gtk-doc.make
autoreconf -fiv

%build
%configure \
    --libexecdir=/usr/lib/lightdm \
    --localstatedir=/var \
    --sbindir=%{_bindir} \
    --sysconfdir=/etc \
    --disable-static \
    --disable-tests \
    --with-greeter-user=lightdm \
    --with-greeter-session=lightdm-gtk-greeter
%make_build

%install
rm -rf %{buildroot}
%make_install

# the session wrapper is part of tests/ and is not installed upstream.
install -Dpm0755 tests/src/lightdm-session %{buildroot}%{_bindir}/lightdm-session
sed -i '1 s/sh/bash --login/' %{buildroot}%{_bindir}/lightdm-session

# Upstart job and AppArmor profiles are for other distributions.
rm -rf %{buildroot}%{_sysconfdir}/init
rm -rf %{buildroot}%{_sysconfdir}/apparmor.d

# The AccountsService interface symlink is dangling without accountsservice,
# which we do not ship.
rm -rf %{buildroot}%{_datadir}/accountsservice

install -Dpm0644 %{SOURCE1} %{buildroot}%{_unitdir}/lightdm.service
install -Dpm0644 %{SOURCE2} %{buildroot}%{_prefix}/lib/systemd/system-preset/50-lightdm.preset

%pre
# Idempotent and tolerant of chroot installs where /dev/null is not mounted
# yet: a failed check must not abort the transaction.
getent group lightdm >/dev/null 2>&1 || groupadd -g 65 lightdm || :
getent passwd lightdm >/dev/null 2>&1 || \
    useradd -c "Lightdm Daemon" -d /var/lib/lightdm -u 65 -g lightdm \
            -s /bin/false lightdm || :

%post
install -dm755 -o lightdm -g lightdm /var/lib/lightdm /var/lib/lightdm-data
install -dm755 -o lightdm -g lightdm /var/cache/lightdm
install -dm770 -o lightdm -g lightdm /var/log/lightdm

# Apply the shipped preset so the display manager replaces getty on tty1.
if [ -x /usr/bin/systemctl ]; then
    systemctl preset lightdm.service >/dev/null 2>&1 || :
fi

%package gir
Summary:    GObject Introspection data for lightdm
License:    GPL-3.0-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for lightdm.  They were installed by the
main package, which is where upstream's build puts them; the .gir
XML needed for building stays there.

%files -f %{_sourcedir}/lightdm.filelist

%files lang -f %{_sourcedir}/lightdm-lang.filelist

%files gir -f %{_sourcedir}/lightdm-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.33.1-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.33.1-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.33.1-2
- Make the %pre user/group creation idempotent and non-fatal: a chroot
  install without /dev/null made the getent guard fail and then aborted
  when groupadd reported the existing group (exit 9)

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.33.1-1
- Package lightdm 1.33.1, replacing the stale 1.24.0 template
- Install a systemd unit and preset (lightdm.service, aliased to
  display-manager.service), lightdm-session wrapper, and the
  lightdm user/group via scriptlets
- Skip the yelp help build (no yelp-tools/itstool), the Upstart job, the
  AppArmor profiles and the dangling AccountsService interface symlink

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.24.0
- Initial RPM
