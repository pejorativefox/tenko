Name:       libseccomp
Version:    2.6.1
Release:    3
Summary:    Seccomp userspace library
License:    LGPL
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Userspace library for the Linux seccomp filter.

%package devel
Summary:    Development files for libseccomp
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in libseccomp; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libseccomp.filelist
%files devel

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 2.6.1-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.6.0
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.6.0
- Bootstrap dependency for man-db/systemd
