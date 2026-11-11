Name:       libxau
Version:    1.0.12
Release:    4
Summary:    X11 authorisation library
License:    MIT-open-group
URL:        https://gitlab.freedesktop.org/xorg/lib/libxau
Source0:    libXau-%{version}.tar.xz
Prefix:     /usr

%description
X11 authorisation library

%prep
%setup -q -n libXau-%{version}

%build 
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxau.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.12-4
- Record the verified license (MIT-open-group): COPYING (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.0.12-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.0.12
- Sync with 1.0.11

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.0.11-1
- Version bump
