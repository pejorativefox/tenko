Name:       xfce-desktop-full
Version:    4.20
Release:    3
Summary:    Tenko XFCE 4.20 full desktop (session + all hardware extras)
License:    MIT
URL:        https://github.com/pejorativefox/tenko
Prefix:     /usr

# The complete install: the existing xfce-desktop meta (session, X11,
# firmware base, hwdb, weak vendor-pack recommendations) plus the
# hardware profile (every firmware vendor pack, Mesa) and a kernel.
Requires:   tenko-base-runtime
Requires:   linux-kernel
Requires:   xfce-desktop
Requires:   xfce-desktop-hardware

%description
The complete Tenko XFCE 4.20 desktop for physical hardware: the
runtime base, a kernel, the full XFCE session from xfce-desktop and the
hardware profile (Mesa, udev hwdb and every linux-firmware vendor pack).

Existing installs can keep using "tenko-base xfce-desktop"; this meta
is the one-shot profile for a laptop or workstation.

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/tenko
touch %{buildroot}/usr/share/tenko/xfce-desktop-full

%files -f %{_sourcedir}/xfce-desktop-full.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 4.20-3
- Drop the browneye marker cleanup; no Browneye installs remain.

* Fri Nov 06 2026 tenko <build@tenko.invalid> 4.20-2
- Use tenko-base-runtime and the /usr/share/tenko marker; clean up the
  old browneye marker on upgrade.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20-1
- New full desktop profile: xfce-desktop + xfce-desktop-hardware +
  runtime base and kernel (plan D25)
