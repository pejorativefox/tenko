Name:       alsa-lib
Version:    1.2.16.1
Release:    3
Summary:    ALSA sound interface library
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
The ALSA Library package contains the ALSA library used by programs
(including ALSA Utilities) requiring access to the ALSA sound interface.
It provides libasound.so.2, which GTK3-based browsers such as Firefox load
at startup even when no output device is used.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/alsa-lib.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.2.16.1-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.16.1-1
- Update to 1.2.16.1 (current base set), replacing the 2018 1.1.6 spec
- Build with --disable-static; ship a generated static filelist
- Needed by firefox-bin (libxul.so links libasound.so.2)
