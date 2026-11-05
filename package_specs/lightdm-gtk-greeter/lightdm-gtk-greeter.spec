Name:       lightdm-gtk-greeter
Version:    2.0.9
Release:    2
Summary:    GTK+ greeter for LightDM
License:    GPL-3.0-or-later
Source0:    lightdm-gtk-greeter-2.0.9.tar.gz
Prefix:     /usr

BuildRequires: gtk+, libxklavier, gettext
# liblightdm-gobject-1.pc, the GIR and the headers come from lightdm.
BuildRequires: lightdm

Requires: lightdm >= 1.19.2

%description
The reference GTK+ greeter for LightDM.  It provides the login screen, the
session/desktop chooser, the keyboard layout menu, and a power menu.

%package lang
Summary:    lightdm-gtk-greeter translations
Requires:   lightdm-gtk-greeter = %{version}-%{release}

%description lang
Translations for the LightDM GTK greeter.

%package doc
Summary:    lightdm-gtk-greeter documentation
Requires:   lightdm-gtk-greeter = %{version}-%{release}

%description doc
Sample greeter stylesheet.

%prep
%setup -q

%build
%configure \
    --libexecdir=/usr/lib/lightdm \
    --sbindir=%{_bindir} \
    --sysconfdir=/etc \
    --with-libxklavier \
    --enable-kill-on-sigterm \
    --disable-libido \
    --disable-libindicator \
    --disable-static \
    --disable-maintainer-mode
%make_build

%install
rm -rf %{buildroot}
%make_install

# BLFS: version the documentation directory.
mv -v %{buildroot}%{_docdir}/lightdm-gtk-greeter \
      %{buildroot}%{_docdir}/lightdm-gtk-greeter-%{version}

%files -f %{_sourcedir}/lightdm-gtk-greeter.filelist

%files lang -f %{_sourcedir}/lightdm-gtk-greeter-lang.filelist

%files doc -f %{_sourcedir}/lightdm-gtk-greeter-doc.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.0.9-2
- Build against lightdm instead of lightdm-devel: the -devel subpackages
  were removed and the .pc/GIR/headers now ship in lightdm (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.0.9-1
- Initial package (BLFS r13.1 lightdm-gtk-greeter 2.0.9)
