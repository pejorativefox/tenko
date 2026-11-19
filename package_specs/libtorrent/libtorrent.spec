Name:       libtorrent
Version:    0.16.28
Release:    1
Summary:    BitTorrent library written in C++ for Unix
License:    GPL-2.0-or-later
URL:        https://github.com/rakshasa/libtorrent
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: curl
BuildRequires: zlib

%description
libtorrent (rakshasa) is a BitTorrent library written in C++ for Unix,
featuring piece-level control, per-torrent rate limiting and
mmap-based piece storage.  It is the library behind the rtorrent
client.  This build installs the shared library, headers and the
libtorrent.pc file.

Note: this is the rakshasa libtorrent used by rtorrent, not arvidn's
libtorrent (libtorrent.org), which is a different project with the
same name.

libtorrent is not part of the base set; it is packaged for rtorrent.

Version 0.16.28 is the latest stable upstream release (tag v0.16.28,
2026-11-11, paired with rtorrent 0.16.28).

%prep
%setup -q

%build
# The release tarball ships no generated configure script.
autoreconf -fi
%configure --disable-debug
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libtorrent.filelist

%changelog
* Fri Nov 20 2026 tenko <build@tenko.invalid> 0.16.28-1
- New package, not in the base set: latest upstream stable release
  (0.16.28, tag v0.16.28, checked 2026-11-20), the companion library
  of rtorrent 0.16.28.  The tarball ships no configure script, so
  autoreconf is run; built with the libcurl and zlib dependencies.
