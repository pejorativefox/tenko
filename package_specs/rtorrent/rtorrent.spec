Name:       rtorrent
Version:    0.16.28
Release:    1
Summary:    Ncurses BitTorrent client based on the libtorrent library
License:    GPL-2.0-or-later
URL:        https://github.com/rakshasa/rtorrent
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: libtorrent
BuildRequires: ncurses
BuildRequires: tinyxml2
BuildRequires: zlib

%description
rtorrent is a console-based BitTorrent client using libtorrent.  It
uses the ncurses interface, supports session management and
fast-resume, and can run in the background in screen/tmux.  XML-RPC
control (for SCGI web frontends such as ruTorrent) is enabled through
tinyxml2.

rtorrent is not part of the base set; the user requested the package.

Version 0.16.28 is the latest stable upstream release (tag v0.16.28,
2026-11-11).

%prep
%setup -q

%build
%configure --with-xmlrpc-tinyxml2
%make_build

%install
rm -rf %{buildroot}
%make_install
install -D -m 0644 doc/rtorrent.rc %{buildroot}/usr/share/doc/rtorrent/rtorrent.rc

%files -f %{_sourcedir}/rtorrent.filelist

%changelog
* Fri Nov 20 2026 tenko <build@tenko.invalid> 0.16.28-1
- New package, not in the base set: latest upstream stable release
  (0.16.28, tag v0.16.28, checked 2026-11-20), paired with
  libtorrent 0.16.28.  Built with ncurses and XML-RPC support via
  tinyxml2; the example configuration ships as
  /usr/share/doc/rtorrent/rtorrent.rc.
