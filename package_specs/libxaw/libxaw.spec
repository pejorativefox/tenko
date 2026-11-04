Name:       libxaw
Version:    1.0.16
Release:    3
Summary:    Xt widget set
License:    MIT
Prefix:     /usr
Source0:    libXaw-1.0.16.tar.xz

BuildRequires: libxmu, libxpm

%description
Xaw is a widget set based on the X Toolkit Intrinsics (Xt) Library.

%package devel
Summary:    Development files for libxaw
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in libxaw; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

%prep
%setup -q -n libXaw-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxaw.filelist
%files devel
%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.0.16-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.0.16
- Sync with BLFS r13.1 (libxaw 1.0.16)
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.0.15-1
- Version bump
