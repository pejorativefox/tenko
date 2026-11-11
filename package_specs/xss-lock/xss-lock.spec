Name:       xss-lock
Version:    0.3.0
Release:    1
Summary:    Use XScreenSaver events to run a session locker
License:    MIT
URL:        https://github.com/xdbob/xss-lock
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: gcc
BuildRequires: cmake
BuildRequires: pkgconf
BuildRequires: glib
BuildRequires: libxcb
BuildRequires: xcb-util
BuildRequires: python3-docutils

Requires:   glib
Requires:   libxcb
Requires:   xcb-util

%description
xss-lock listens for XScreenSaver events and runs a locker such as
light-locker or xfce4-screensaver when the X11 screen saver activates or the
system is about to suspend.  It also watches logind PrepareForSleep signals
so the session can be locked before suspend.

%prep
%setup -q

%build
# Upstream still declares cmake_minimum_required(VERSION 2.8), which CMake 4
# refuses; keep compatibility enabled for this unmaintained release.
cmake -S . -B build \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build build --parallel %{_smp_build_ncpus}

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} cmake --install build

%files -f %{_sourcedir}/xss-lock.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 0.3.0-1
- Initial package.  xss-lock is not in the base set.
- Version 0.3.0 is the latest stable upstream release (GitHub tag v0.3.0,
  2016-09-21); the project has not published a newer release.
- Source: https://github.com/xdbob/xss-lock/archive/refs/tags/v0.3.0.tar.gz
  md5 ebfa58416117a272c2e534036a0deeb4
  sha256 2beb7d05991b4fba341dcdf2d8160253e694a7ee47eb2eb0eade59dd5ce7ca18
- Build with CMake and install the man page, bash/zsh completion and the
  example scripts from doc/.  Set CMAKE_POLICY_VERSION_MINIMUM=3.5 because
  the unmaintained upstream still declares cmake_minimum_required(VERSION
  2.8), which CMake 4 rejects.
