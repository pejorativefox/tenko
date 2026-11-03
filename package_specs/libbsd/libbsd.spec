Name:       libbsd
Version:    0.12.2
Release:    2
Summary:    BSD compatibility library
License:    BSD
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
BSD compatibility library used by shadow (readpassphrase).

%package devel
Summary:    Development files for libbsd
Requires:   %{name} = %{version}-%{release}

%description devel
pkg-config files for libbsd, used to build software against it.

%prep
%setup -q

%build
%configure --disable-static --without-libbsd
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libbsd.filelist
%files devel -f %{_sourcedir}/libbsd-devel.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.12.2-2
- Move the pkg-config files into a new -devel subpackage so the runtime
  package no longer drags pkgconfig(...) consumers into every install.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.12.2
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 0.12.2
- Bootstrap dependency for shadow
