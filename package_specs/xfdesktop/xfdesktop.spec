Name:       xfdesktop
Version:    4.20.2
Release:    3
Summary:    A desktop manager for Xfce
License:    GPL-2.0-or-later
URL:        https://docs.xfce.org/xfce/xfdesktop/start
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: exo
BuildRequires: garcon
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: harfbuzz
BuildRequires: libnotify
BuildRequires: libx11
BuildRequires: libxfce4ui
BuildRequires: libxfce4util
BuildRequires: libxfce4windowing
BuildRequires: pango
BuildRequires: thunar
BuildRequires: xfconf

%description
A desktop manager for Xfce

%package lang
Summary:    xfdesktop translations
Requires:   xfdesktop = %{version}-%{release}

%description lang
Translations for xfdesktop.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfdesktop.filelist
%files lang -f %{_sourcedir}/xfdesktop-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.2-3
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.2-2
- Split lang payload into xfdesktop-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.2
- Sync with 4.19.1

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.1
- Initial RPM

