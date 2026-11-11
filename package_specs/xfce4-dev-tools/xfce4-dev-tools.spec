Name:       xfce4-dev-tools
Version:    4.20.0
Release:    2
Summary:    Collection of tools and macros for Xfce developers
License:    GPL-2.0-or-later
URL:        https://docs.xfce.org/xfce/xfce4-dev-tools/start
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr
BuildRequires: libxslt

%description
The Xfce development tools are a collection of tools and macros for Xfce developers and people that want to build Xfce from Git In addition it contains the Xfce developer's handbook.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfce4-dev-tools.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.0-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING (issue #8).

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with 4.19.0

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.0
- Initial RPM

