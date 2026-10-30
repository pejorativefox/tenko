Name:       browneye-sysconfig
Version:    13.1
Release:    1
Summary:    Base configuration for Browneye Linux
License:    MIT
Prefix:     /usr

%description
Base configuration files for Browneye Linux.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc %{buildroot}/etc/systemd/system/getty.target.wants
ln -sf /usr/lib/systemd/system/multi-user.target %{buildroot}/etc/systemd/system/default.target
ln -sf /usr/lib/systemd/system/serial-getty@ttyS0.service %{buildroot}/etc/systemd/system/getty.target.wants/serial-getty@ttyS0.service
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

%files
/etc/fstab
/etc/systemd/system/default.target
/etc/systemd/system/getty.target.wants/serial-getty@ttyS0.service
/etc/hosts
/etc/shells
/etc/inputrc
/etc/vimrc
/etc/profile

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 13.1
- Base configuration for LFS r13.1
