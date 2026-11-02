Name:       libpsl
Version:    0.23.3
Release:    1
Summary:    Public Suffix List library
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
libpsl provides access to the Public Suffix List (a set of domain names
beyond the standard suffixes such as .com).  curl uses it to enforce
cookie and HSTS scoping correctly.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release
ninja %{?_smp_mflags}
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libpsl.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.23.3-1
- New package (D8): current BLFS trunk version, built with libidn2; curl is
  rebuilt with PSL support instead of --without-libpsl.
