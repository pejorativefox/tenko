Name:       tenko-sysconfig
Version:    13.1
Release:    4
# Tenko rename compatibility (issue #22).
Obsoletes: browneye-sysconfig < 13.1-4
Provides: browneye-sysconfig = %{version}-%{release}
Summary:    Base configuration for Tenko Linux
License:    MIT
Prefix:     /usr

%description
Base configuration files for Tenko Linux.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc %{buildroot}/etc/systemd/system/getty.target.wants
mkdir -p %{buildroot}/etc/systemd/journald.conf.d %{buildroot}/etc/systemd/network
mkdir -p %{buildroot}/etc/dracut.conf.d
ln -sf /usr/lib/systemd/system/multi-user.target %{buildroot}/etc/systemd/system/default.target
ln -sf /usr/lib/systemd/system/serial-getty@ttyS0.service %{buildroot}/etc/systemd/system/getty.target.wants/serial-getty@ttyS0.service

# Locale and console defaults (LFS chapter 9).
cat > %{buildroot}/etc/locale.conf <<'EOF2'
LANG=C.UTF-8
EOF2
cat > %{buildroot}/etc/vconsole.conf <<'EOF2'
KEYMAP=us
EOF2

# Keep journals across reboots but bound their size.
cat > %{buildroot}/etc/systemd/journald.conf.d/10-tenko.conf <<'EOF2'
[Journal]
Storage=persistent
SystemMaxUse=512M
RuntimeMaxUse=64M
EOF2

# Generic initramfs: the installed image must boot hardware other than the
# machine that ran dracut, so include all storage/filesystem drivers instead
# of only the build host's.  xz matches the kernel module compression and is
# already in the base system.
cat > %{buildroot}/etc/dracut.conf.d/10-tenko.conf <<'EOF2'
hostonly="no"
compress="xz"
EOF2

# DHCP on the usual wired interfaces; systemd-networkd/resolved are enabled
# by "systemctl preset-all" during rootfs assembly.
cat > %{buildroot}/etc/systemd/network/10-dhcp.network <<'EOF2'
[Match]
Name=en* eth*

[Network]
DHCP=yes
EOF2
ln -sf /run/systemd/resolve/stub-resolv.conf %{buildroot}/etc/resolv.conf

# Empty by design: systemd generates a unique id on first boot.
: > %{buildroot}/etc/machine-id

# Rootless containers: useradd/usermod only allocate subordinate id ranges
# when these files exist (login.defs already defines SUB_UID/GID_*).
cat > %{buildroot}/etc/subuid <<'EOF2'
# Per-user subordinate UID ranges for rootless containers.
EOF2
cat > %{buildroot}/etc/subgid <<'EOF2'
# Per-user subordinate GID ranges for rootless containers.
EOF2
chmod 0444 %{buildroot}/etc/machine-id
cat > %{buildroot}/etc/hosts <<'EOF2'
127.0.0.1 localhost
::1       localhost
EOF2
cat > %{buildroot}/etc/shells <<'EOF2'
/bin/sh
/bin/bash
EOF2
cat > %{buildroot}/etc/inputrc <<'EOF2'
set bell-style none
"\e[1~": beginning-of-line
"\e[4~": end-of-line
EOF2
cat > %{buildroot}/etc/vimrc <<'EOF2'
set nocompatible
set backspace=2
syntax on
EOF2
cat > %{buildroot}/etc/fstab <<'EOF2'
# <file system> <mount point> <type> <options> <dump> <pass>
tmpfs /tmp tmpfs defaults 0 0
EOF2
cat > %{buildroot}/etc/profile <<'EOF2'
export PS1='(\h) \u:\w\$ '
alias ls='ls --color'
for f in /etc/profile.d/*.sh; do
    [ -r "$f" ] && . "$f"
done
unset f
EOF2

%post
# Remove old %%config(noreplace) configuration files.
rm -f /etc/dracut.conf.d/10-browneye.conf
rm -f /etc/systemd/journald.conf.d/10-browneye.conf

%files
/etc/fstab
/etc/systemd/system/default.target
/etc/systemd/system/getty.target.wants/serial-getty@ttyS0.service
/etc/systemd/journald.conf.d/10-tenko.conf
%dir /etc/systemd/journald.conf.d
%dir /etc/dracut.conf.d
%config(noreplace) /etc/dracut.conf.d/10-tenko.conf
/etc/systemd/network/10-dhcp.network
/etc/hosts
/etc/shells
/etc/inputrc
/etc/vimrc
%config(noreplace) /etc/subuid
%config(noreplace) /etc/subgid
/etc/profile
/etc/locale.conf
/etc/vconsole.conf
/etc/resolv.conf
/etc/machine-id

%changelog
* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-4
- Rename browneye-sysconfig to tenko-sysconfig and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-3
- Ship /etc/subuid and /etc/subgid: useradd/usermod only allocate
  subordinate id ranges when the files exist, so rootless podman had no
  mapping for the installer-created admin user

* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-2
- Add /etc/dracut.conf.d/10-browneye.conf: generic (hostonly=no) initramfs,
  xz-compressed, matching the kernel's module compression

* Sat Oct 31 2026 browneye <build@browneye.invalid> 13.1
- Add locale/vconsole, journald, networkd, resolv.conf, and machine-id defaults

* Fri Oct 30 2026 browneye <build@browneye.invalid> 13.1
- Base configuration for LFS r13.1
