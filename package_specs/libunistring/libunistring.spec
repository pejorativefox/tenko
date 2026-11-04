Name:       libunistring
Version:    1.5
Release:    1
Summary:    GNU Unicode string library
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
libunistring provides functions for manipulating Unicode strings and for
manipulating C strings according to the Unicode standard.  It is a build
dependency of libidn2 (and through it libpsl and curl/rsync IDN support).

%prep
%setup -q

%build
%configure --disable-static --docdir=/usr/share/doc/libunistring-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libunistring.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.5-1
- New package (D8): current BLFS trunk version, needed by libidn2.
