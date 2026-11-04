Name:       libxau
Version:    1.0.12
Release:    3
Summary:    X11 authorisation library
License:    GPL3
Source0:    libXau-%{version}.tar.xz
Prefix:     /usr

%description
X11 authorisation library

%package devel
Summary:    Development files for libxau
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in libxau; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

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
%files devel


%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.0.12-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.0.12
- Sync with BLFS r13.1 (1.0.11)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.0.11-1
- Version bump
