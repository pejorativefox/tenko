Name:       steam-devices
Version:    20260625
Release:    1
Summary:    Udev rules for Steam and game controller devices
License:    MIT
URL:        https://github.com/ValveSoftware/steam-devices
Prefix:     /usr
BuildArch:  noarch
Source0:    steam-devices-%{version}.tar.gz

# The rules are only useful when udev is present to apply them; systemd owns
# udevadm and /usr/lib/udev/rules.d.
Requires:   systemd

%description
Valve's udev rules for Steam-related hardware.  They grant the active local
user read/write access to /dev/uinput, Valve HID devices and a range of
game controllers and VR headsets used by Steam, SteamVR, Wine, Lutris and
other game launchers.

This package carries a snapshot of upstream master at commit 22ec85e
(2026-06-25).  Upstream's newest tag is v1.0.0.61 from 2019, which predates
current controllers; Fedora and RPM Fusion package the same current rules.

The Steam Flatpak checks /dev/uinput and warns when the user cannot read and
write it.  Without these rules the node stays root-only.

%prep
%setup -q -n steam-devices-22ec85e5ff5ea2e15c56d71a41bcbef46356cd60

%build

%install
rm -rf %{buildroot}
install -Dpm0644 60-steam-input.rules \
    %{buildroot}%{_udevrulesdir}/60-steam-input.rules
install -Dpm0644 60-steam-vr.rules \
    %{buildroot}%{_udevrulesdir}/60-steam-vr.rules

%post
# No udev file trigger exists in this systemd package, so reload the rules and
# reapply them to the existing uinput node.  Without this the active user
# keeps the old root-only permissions until the next boot.
if [ -x /usr/bin/udevadm ]; then
    /usr/bin/udevadm control --reload >/dev/null 2>&1 || :
    /usr/bin/udevadm trigger --action=change --subsystem-match=misc \
        --sysname-match=uinput >/dev/null 2>&1 || :
fi

%files
%license LICENSE
%{_udevrulesdir}/60-steam-input.rules
%{_udevrulesdir}/60-steam-vr.rules

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 20260625-1
- New package: Valve's Steam device udev rules, snapshot of
  ValveSoftware/steam-devices master at 22ec85e (2026-06-25).  Upstream has
  no release newer than v1.0.0.61 (2019), whose rules predate current
  controllers; the master rules are the set Fedora and RPM Fusion ship.
  They grant the active local user read/write access to /dev/uinput and the
  supported controller hidraw/evdev nodes, which is what the Steam Flatpak
  wrapper checks before warning that "steam-devices" is missing.
