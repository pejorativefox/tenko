Name:       tenko-firstboot
Version:    6
Release:    3
Epoch:      1
Summary:    First-boot root account policy for Tenko Linux
License:    MIT
Prefix:     /usr
Requires:   shadow
Requires:   systemd

%description
Tenko ships the root account locked.  This package adds a one-shot
service that, on the first boot where root has no usable password, prompts
on tty1 for a new root password with passwd(1).  It is idempotent: an image
that already has a root password (such as the QEMU test image, root/root)
is detected and skipped, and a marker records that the policy has run.

%prep

%build

%install
rm -rf %{buildroot}

install -vdm755 %{buildroot}%{_libexecdir}
install -vm755 %{_sourcedir}/tenko-firstboot-root-password \
    %{buildroot}%{_libexecdir}/tenko-firstboot-root-password

install -vdm755 %{buildroot}%{_unitdir}
install -vm644 %{_sourcedir}/tenko-firstboot-root-password.service \
    %{buildroot}%{_unitdir}/tenko-firstboot-root-password.service

install -vdm755 %{buildroot}/usr/lib/systemd/system-preset
install -vm644 %{_sourcedir}/90-tenko-firstboot.preset \
    %{buildroot}/usr/lib/systemd/system-preset/90-tenko-firstboot.preset

install -vdm755 %{buildroot}%{_docdir}/tenko-firstboot
install -vm644 %{_sourcedir}/README \
    %{buildroot}%{_docdir}/tenko-firstboot/README

install -vdm755 %{buildroot}/var/lib/tenko

%post
if command -v systemctl >/dev/null 2>&1; then
    systemctl --root=/ enable tenko-firstboot-root-password.service \
        >/dev/null 2>&1 || true
fi

%files -f %{_sourcedir}/tenko-firstboot.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-3
- Keep only the ordering against kmsconvt@tty1.service; drop the Conflicts=.
  systemd enqueues a stop job for a Conflicts= target even when this unit's
  first-boot ConditionPathExists is false, and that deleted kmscon's start
  job on every normal boot.  Before= still keeps the prompt on tty1 until it
  exits.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-2
- Conflict with and start before kmsconvt@tty1.service, so the first-boot
  root password prompt keeps tty1 now that kmscon is the base console.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-1
- Rebase on the Tenko 6 distro release with Epoch 1 so installs carrying
  the old 13.1 EVR upgrade cleanly.
- Drop the browneye-firstboot Obsoletes/Provides alias and the old marker,
  unit and preset cleanup; no Browneye installs remain.

* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-3
- Rename browneye-firstboot to tenko-firstboot and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-2
- Order the prompt Before=display-manager.service: with LightDM installed
  the greeter would otherwise take tty1 while passwd(1) was still waiting

* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-1
- First-boot root password policy (E5): tty1-only oneshot, idempotent,
  skipped when root already has a password
