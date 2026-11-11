Name:       nano
Version:    9.3
Release:    1
Summary:    Small and friendly text editor
License:    GPL-3.0-or-later
URL:        https://www.nano-editor.org/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: ncurses
BuildRequires: gettext
BuildRequires: groff

%description
GNU nano is a small, friendly text editor inspired by Pico.  It provides
full-screen editing, syntax highlighting, search and replace, undo and redo,
and UTF-8 support while remaining small enough for minimal systems.  This
build enables nanorc configuration files, colour syntax highlighting and
UTF-8 input, installs the rnano restricted wrapper, and ships the upstream
syntax definitions under /usr/share/nano.

%prep
%setup -q

%build
%configure --enable-nanorc --enable-utf8 --enable-color
%make_build

%install
rm -rf %{buildroot}
%make_install

# The info index is generated on the target system, not shipped.
rm -f %{buildroot}%{_infodir}/dir

# Upstream only ships a sample; install it as the system-wide nanorc and
# enable the installed syntax definitions by default.
install -Dm644 doc/sample.nanorc %{buildroot}%{_sysconfdir}/nanorc
sed -i 's|^# include /usr/share/nano/\*.nanorc|include /usr/share/nano/*.nanorc|' \
    %{buildroot}%{_sysconfdir}/nanorc

%files -f %{_sourcedir}/nano.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 9.3-1
- Initial package at the latest stable upstream release, GNU nano 9.3
  (published 2026-10-21), from the upstream release tarball.
- Licence verified as GPL-3.0-or-later from COPYING (GNU GPL version 3)
  and the source headers ("version 3 ... or (at your option) any later
  version").
- Build with nanorc support, colour syntax highlighting and UTF-8 input.
  Ship the upstream sample as /etc/nanorc (%config(noreplace)), with the
  /usr/share/nano/*.nanorc include enabled, plus /usr/share/nano syntax
  files and the rnano wrapper installed by upstream.
