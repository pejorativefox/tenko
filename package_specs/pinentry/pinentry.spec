Name:       pinentry
Version:    1.3.3
Release:    1
Summary:    Passphrase entry dialogs for GnuPG
License:    GPL-2.0-or-later
URL:        https://gnupg.org/software/pinentry/
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: libgpg-error
BuildRequires: libassuan
BuildRequires: ncurses
BuildRequires: gcr
BuildRequires: libsecret

%description
pinentry is the set of dialogs gpg-agent uses to ask for passphrases and
PINs.  The package ships the curses and tty dialogs and the GNOME 3 dialog,
which uses the gcr prompter and can save a passphrase in the login keyring
through libsecret.  /usr/bin/pinentry is the GNOME 3 dialog; it falls back
to curses when there is no graphical session.

%prep
%setup -q

%build
%configure \
    --enable-pinentry-curses \
    --enable-fallback-curses \
    --enable-pinentry-tty \
    --enable-pinentry-gnome3 \
    --enable-libsecret \
    --disable-pinentry-emacs \
    --disable-pinentry-efl \
    --disable-pinentry-gtk2 \
    --disable-pinentry-qt \
    --disable-pinentry-qt5 \
    --disable-pinentry-qt4 \
    --disable-pinentry-tqt \
    --disable-pinentry-fltk
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -f %{buildroot}%{_infodir}/dir
# gpg-agent runs /usr/bin/pinentry; it must be the GNOME 3 dialog.
[ "$(readlink %{buildroot}%{_bindir}/pinentry)" = pinentry-gnome3 ]

%files -f %{_sourcedir}/pinentry.filelist

%changelog
* Mon Nov 16 2026 tenko <build@tenko.invalid> 1.3.3-1
- New package, not in the base set: latest upstream stable release
  (1.3.3, checked 2026-11-16).  Without a pinentry gpg-agent cannot ask for
  a passphrase.
- Ships the curses, tty and GNOME 3 dialogs; /usr/bin/pinentry is the
  GNOME 3 dialog with the curses fallback, and libsecret caching is on.
