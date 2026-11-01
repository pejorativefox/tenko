Name:       xfce4-session
Version:    4.20.4
Release:    2
Summary:    A session manager for Xfce
License:    GPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: iceauth

%description
A session manager for Xfce

%package lang
Summary:    xfce4-session translations
Requires:   xfce4-session = %{version}-%{release}

%description lang
Translations for xfce4-session.

%prep
%setup

%build
%configure --disable-legacy-sm
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfce4-session.filelist
%files lang -f %{_sourcedir}/xfce4-session-lang.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.4-2
- Split lang payload into xfce4-session-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.4
- Sync with BLFS r13.1 (4.19.1)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

