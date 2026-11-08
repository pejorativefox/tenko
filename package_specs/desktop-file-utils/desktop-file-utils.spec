Name:       desktop-file-utils
Version:    0.28
Release:    3
Summary:    Utilities for working with desktop entries
License:    GPL-2.0-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
Utilities for validating and updating desktop entries and the MIME database.

%prep
%setup -q

%build
rm -fv /usr/bin/desktop-file-edit
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/desktop-file-utils.filelist

# Keep the desktop entry database in sync with every transaction that
# installs, upgrades or erases an application entry.  Package scriptlets no
# longer need to call update-desktop-database by hand.
%transfiletriggerin -- %{_datadir}/applications
update-desktop-database -q %{_datadir}/applications &>/dev/null || :

%transfiletriggerpostun -- %{_datadir}/applications
update-desktop-database -q %{_datadir}/applications &>/dev/null || :

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 0.28-3
- Add file triggers for /usr/share/applications so installing or removing
  any package refreshes the desktop entry database without ad-hoc %post
  calls (issue #35).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.28-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING and src/validate.c (issue #8).

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.28
- Initial package
