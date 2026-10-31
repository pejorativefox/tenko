Name:       libbsd
Version:    0.12.2
Release:    1
Summary:    BSD compatibility library
License:    BSD
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
BSD compatibility library used by shadow (readpassphrase).

%prep
%setup -q

%build
%configure --disable-static --without-libbsd
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libbsd.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.12.2
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 0.12.2
- Bootstrap dependency for shadow
