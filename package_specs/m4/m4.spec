Name:       m4
Version:    1.4.21
Release:    2
Summary:    M4 macro processor
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
TODO

%package lang
Summary:    m4 translations
Requires:   m4 = %{version}-%{release}

%description lang
Translations for m4.

%prep
%setup -q -a0

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/m4.filelist
%files lang -f %{_sourcedir}/m4-lang.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.4.21-2
- Split lang payload into m4-lang (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.4.21
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.4.19
- Version bump
