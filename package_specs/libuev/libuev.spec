Name:       libuev
Version:    2.4.1
Release:    1
Summary:    Simple event loop for Linux
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
Lightweight event loop library for Linux epoll() family APIs

%prep
%setup -q

%build
%configure
%make_build

%install
%make_install

%files -f %{_sourcedir}/libuev.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.4.1-1
- Update 2.4.0 -> 2.4.1.
- Basis: not in the r13.1 book; latest upstream stable 2026-11-05
  (libuev 2.4.1, released 2024-01-04).
- Source: https://github.com/troglobit/libuev/releases/download/v2.4.1/libuev-2.4.1.tar.xz
  md5 a5f6bdb0c244451d63ec180627cdfd19
- Autotools build; the library is self-contained and does not need
  libev.
- Static filelist generated from the install tree.
