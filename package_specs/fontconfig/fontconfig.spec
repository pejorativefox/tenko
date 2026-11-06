Name:       fontconfig
Version:    2.18.3
Release:    4
Summary:    Font access library
License:    HPND
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: freetype >= 2.13.1

%description
The Fontconfig package contains a library and support programs used for configuring and customizing font access.

%prep
%setup -q

%build
rm -f src/fcobjshash.h
%configure  --sysconfdir=/etc    \
            --localstatedir=/var \
            --disable-docs       \
            --docdir=/usr/share/doc/fontconfig-%{version}
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/fontconfig.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.18.3-4
- Record the verified license (HPND): COPYING and src/fcxml.c (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.18.3-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.18.3-2
- Split devel payload into fontconfig-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.18.3
- Sync with 2.13.1

# let's skip this for now
