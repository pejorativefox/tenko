Name:       browneye-firstboot
Version:    13.1
Release:    1
Summary:    First-boot root account policy for Browneye Linux
License:    MIT
Prefix:     /usr
Requires:   shadow
Requires:   systemd

%description
Browneye ships the root account locked.  This package adds a one-shot
service that, on the first boot where root has no usable password, prompts
on tty1 for a new root password with passwd(1).  It is idempotent: an image
that already has a root password (such as the QEMU test image, root/root)
is detected and skipped, and a marker records that the policy has run.

%prep

%build

%install
rm -rf %{buildroot}

install -vdm755 %{buildroot}%{_libexecdir}
install -vm755 %{_sourcedir}/browneye-firstboot-root-password \
    %{buildroot}%{_libexecdir}/browneye-firstboot-root-password

install -vdm755 %{buildroot}%{_unitdir}
install -vm644 %{_sourcedir}/browneye-firstboot-root-password.service \
    %{buildroot}%{_unitdir}/browneye-firstboot-root-password.service

install -vdm755 %{buildroot}/usr/lib/systemd/system-preset
install -vm644 %{_sourcedir}/90-browneye-firstboot.preset \
    %{buildroot}/usr/lib/systemd/system-preset/90-browneye-firstboot.preset

install -vdm755 %{buildroot}%{_docdir}/browneye-firstboot
install -vm644 %{_sourcedir}/README \
    %{buildroot}%{_docdir}/browneye-firstboot/README

install -vdm755 %{buildroot}/var/lib/browneye

%files
/usr/libexec/browneye-firstboot-root-password
/usr/lib/systemd/system/browneye-firstboot-root-password.service
/usr/lib/systemd/system-preset/90-browneye-firstboot.preset
/usr/share/doc/browneye-firstboot/README
%dir /var/lib/browneye

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-1
- First-boot root password policy (E5): tty1-only oneshot, idempotent,
  skipped when root already has a password
