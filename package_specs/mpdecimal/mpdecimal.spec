Name:       mpdecimal
Version:    4.0.1
Release:    3
Summary:    Decimal floating point library
License:    BSD
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
libmpdec is a library for arbitrary precision correctly rounded decimal
floating point arithmetic.

%package devel
Summary:    Development files for mpdecimal
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in mpdecimal; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

%prep
%setup -q

%build
%configure --disable-static --docdir=%{_docdir}/%{name}-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/mpdecimal.filelist
%files devel

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 4.0.1-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.0.1
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.0.1
- Initial package (LFS r13.1)
