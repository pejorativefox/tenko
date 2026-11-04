Name:       xfce-desktop-full
Version:    4.20
Release:    1
Summary:    Browneye XFCE 4.20 full desktop (session + all hardware extras)
License:    MIT
Prefix:     /usr

# The complete install: the existing xfce-desktop meta (session, X11,
# firmware base, hwdb, weak vendor-pack recommendations) plus the
# hardware profile (every firmware vendor pack, Mesa) and a kernel.
Requires:   browneye-base-runtime
Requires:   linux-kernel
Requires:   xfce-desktop
Requires:   xfce-desktop-hardware

%description
The complete Browneye XFCE 4.20 desktop for physical hardware: the
runtime base, a kernel, the full XFCE session from xfce-desktop and the
hardware profile (Mesa, udev hwdb and every linux-firmware vendor pack).

Existing installs can keep using "browneye-base xfce-desktop"; this meta
is the one-shot profile for a laptop or workstation.

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/browneye
touch %{buildroot}/usr/share/browneye/xfce-desktop-full

%files
/usr/share/browneye/xfce-desktop-full

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20-1
- New full desktop profile: xfce-desktop + xfce-desktop-hardware +
  runtime base and kernel (plan D25)
