Name:       fontconfig
Version:    2.18.3
Release:    1
Summary:    Font access library
License:    GPL3
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
* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.18.3
- Sync with BLFS r13.1 (2.13.1)

# let's skip this for now
