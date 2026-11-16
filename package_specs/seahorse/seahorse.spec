Name:       seahorse
Version:    47.0.1
Release:    1
Summary:    Passwords and keys manager for the login keyring
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
URL:        https://gitlab.gnome.org/GNOME/seahorse
Source0:    %{name}-%{version}.tar.xz
# gpgme 2 removed the trust item API and its GPGME_EVENT_NEXT_TRUSTITEM
# event, which Seahorse only listed among the events it ignores.
Patch0:     %{name}-%{version}-gpgme2.patch
# The PGP backend names the key server source type even when key server
# support is off, which leaves an undefined symbol at link time.
Patch1:     %{name}-%{version}-no-keyserver.patch
Prefix:     /usr

BuildRequires: meson
BuildRequires: ninja
BuildRequires: vala
BuildRequires: gettext
BuildRequires: glib
BuildRequires: gtk+
BuildRequires: libhandy
BuildRequires: gcr
BuildRequires: libsecret
BuildRequires: libpwquality
BuildRequires: gpgme
BuildRequires: gnupg
BuildRequires: openssh
BuildRequires: p11-kit
BuildRequires: desktop-file-utils

# Seahorse runs gpg, ssh-keygen and ssh-add, and talks to the Secret Service
# provider; rpm sees none of these.
Requires:   gnupg
Requires:   openssh
Requires:   gnome-keyring

%description
Seahorse (Passwords and Keys) manages the secrets stored in the login
keyring: it lists and edits stored passwords, locks and unlocks keyrings,
and changes a keyring's password.  It also manages OpenPGP keys, SSH keys
and PKCS#11 certificates.

%prep
%setup -q
%patch -P 0 -p1
%patch -P 1 -p1

%build
mkdir build
pushd build
meson setup ..                      \
      --prefix=/usr                 \
      --libdir=/usr/lib64           \
      --buildtype=release           \
      -Dhelp=false                  \
      -Dmanpage=false               \
      -Dpgp-support=true            \
      -Dpkcs11-support=true         \
      -Dkeyservers-support=false    \
      -Dhkp-support=false           \
      -Dldap-support=false          \
      -Dkey-sharing=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/seahorse.filelist

%changelog
* Mon Nov 16 2026 tenko <build@tenko.invalid> 47.0.1-1
- New package, not in the base set: latest upstream stable release
  (47.0.1, checked 2026-11-16).  It is the desktop's keyring manager: view
  stored secrets and change the login keyring password.
- Built without key server support (HKP needs libsoup 3, LDAP needs
  OpenLDAP; neither is packaged), DNS-SD key sharing, the help pages
  (yelp-tools is not packaged) and the man page.
- Patch out the GPGME_EVENT_NEXT_TRUSTITEM case so the PGP backend builds
  with gpgme 2, and guard the key server source type so the build links
  without key server support.
