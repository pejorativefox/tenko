Name:       gnome-keyring
Version:    50.0
Release:    1
Summary:    Secret Service provider and keyring daemon
License:    LGPL-2.1-or-later AND GPL-2.0-or-later
URL:        https://wiki.gnome.org/Projects/GnomeKeyring
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

BuildRequires: meson
BuildRequires: ninja
BuildRequires: gcc
BuildRequires: gettext
BuildRequires: glib
BuildRequires: gcr
BuildRequires: libgcrypt
BuildRequires: libcap-ng
BuildRequires: p11-kit
BuildRequires: systemd
BuildRequires: linux-pam

Requires:   glib
Requires:   gcr
Requires:   libgcrypt
Requires:   libcap-ng
Requires:   p11-kit
Requires:   linux-pam

%description
gnome-keyring provides the Secret Service API implementation used by
libsecret applications, together with the login keyring, a PKCS#11 module
and a PAM module that unlocks the login keyring with the user's password.
The package also ships the xdg-desktop-portal Secret backend.

Tenko uses it as the desktop's Secret Service provider so applications do
not fall back to plaintext storage.

%prep
%setup -q

%build
mkdir _build
pushd _build
meson setup ..                 \
      --prefix=/usr            \
      --libdir=/usr/lib64      \
      --buildtype=release      \
      -Dmanpage=false          \
      -Dssh-agent=false        \
      -Dselinux=disabled       \
      -Dlibcap-ng=enabled      \
      -Dpam=true               \
      -Dsystemd=enabled        \
      -Ddebug-mode=false
ninja
popd

%install
rm -rf %{buildroot}
pushd _build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/gnome-keyring.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 50.0-1
- New package: gnome-keyring 50.0, the latest stable upstream release
  (2026-03-15), as Tenko's Secret Service provider (issue #39).
- Ship the Secret Service and portal Secret D-Bus activation files, the
  login keyring daemon, the PKCS#11 module and the PAM module.  The PAM
  module is wired into LightDM so the login keyring unlocks with the user's
  password.
- Built without the SSH agent, SELinux support and man pages: the SSH agent
  is out of scope for the Secret Service work, Tenko does not package
  libselinux, and the base build image has no xsltproc/DocBook stylesheet.
