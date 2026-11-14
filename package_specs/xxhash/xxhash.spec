Name:       xxhash
Version:    0.8.4
Release:    1
Summary:    Extremely fast non-cryptographic hash algorithm
License:    BSD-2-Clause AND GPL-2.0-or-later
URL:        https://xxhash.com/
Source0:    xxHash-%{version}.tar.gz
Prefix:     /usr

BuildRequires: gcc
BuildRequires: make

%description
xxHash is an extremely fast non-cryptographic hash algorithm (XXH32,
XXH64 and XXH3).  This package ships the libxxhash shared library, its
headers and pkg-config file (BSD-2-Clause), and the xxhsum command line
tool (GPL-2.0-or-later).  kitty uses it for its rsync-based file transfer
and image caching.

%prep
%setup -q -n xxHash-%{version}

%build
%make_build PREFIX=%{_prefix} LIBDIR=%{_libdir} MANDIR=%{_mandir}/man1

%install
rm -rf %{buildroot}
%make_install PREFIX=%{_prefix} LIBDIR=%{_libdir} MANDIR=%{_mandir}/man1
rm -f %{buildroot}%{_libdir}/libxxhash.a

%check
make test-xxhsum-c

%files -f %{_sourcedir}/xxhash.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 0.8.4-1
- New package, not in the base set: latest upstream stable release (0.8.4,
  checked 2026-11-14).  Needed by kitty.
