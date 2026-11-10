Name:       xfce4-power-manager
Version:    4.20.1
Release:    4
Summary:    Power manager for Xfce desktop
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.bz2
Patch0:     %{name}-%{version}-logind-lid-switch.patch
Prefix:     /usr

%description
Power manager for Xfce desktop

%package lang
Summary:    xfce4-power-manager translations
Requires:   xfce4-power-manager = %{version}-%{release}

%description lang
Translations for xfce4-power-manager.

%prep
%setup -q
%patch -P 0 -p1

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfce4-power-manager.filelist
%files lang -f %{_sourcedir}/xfce4-power-manager-lang.filelist


%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 4.20.1-4
- Default logind-handle-lid-switch to TRUE.  Tenko owns the lid policy in
  systemd-logind (/etc/systemd/logind.conf.d/10-lid-switch.conf from
  tenko-sysconfig), but xfce4-power-manager was claiming handle-lid-switch
  with a block inhibitor, and logind stands down as soon as a block
  inhibitor is present.  Closing the lid therefore only ran the XFCE lid
  action, whose built-in default is "lock screen" (and no screen locker is
  installed), so the laptop never slept.  The setting is still overridable
  per user with "xfconf-query -c xfce4-power-manager -p
  /xfce4-power-manager/logind-handle-lid-switch -n -t bool -s false"; the
  XFCE lid action only applies again with that override.  The change takes
  effect when the power manager restarts at the next login (or with
  "xfce4-power-manager --restart").

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.1-3
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.1-2
- Split lang payload into xfce4-power-manager-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.1
- Sync with 4.19.1

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.6.5
- Initial RPM

