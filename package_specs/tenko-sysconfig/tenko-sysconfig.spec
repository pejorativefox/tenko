Name:       tenko-sysconfig
Version:    6
Release:    7
Epoch:      1
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
mkdir -p %{buildroot}/etc/dracut.conf.d %{buildroot}/etc/skel
ln -sf /usr/lib/systemd/system/multi-user.target %{buildroot}/etc/systemd/system/default.target
ln -sf /usr/lib/systemd/system/serial-getty@ttyS0.service %{buildroot}/etc/systemd/system/getty.target.wants/serial-getty@ttyS0.service

# Locale and console defaults.
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
# The installer creates the admin account in wheel and keeps root locked.
# Make that group the polkit administrator for auth_admin actions; the
# accountsservice rule still adds adm for compatibility.
mkdir -p %{buildroot}/etc/polkit-1/rules.d
chmod 0750 %{buildroot}/etc/polkit-1/rules.d
cat > %{buildroot}/etc/polkit-1/rules.d/50-tenko-wheel.rules <<'EOF2'
// Tenko: the installer adds the admin user to wheel and locks root.
polkit.addAdminRule(function(action, subject) {
    return ["unix-group:wheel"];
});
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
# System-wide interactive shell defaults.  /etc/profile is the only startup
# file a login shell reads; terminal emulators start interactive non-login
# shells, which read ~/.bashrc instead.  Both paths load this file so the
# prompt, aliases and completions are defined once for the whole system.
cat > %{buildroot}/etc/bashrc <<'EOF2'
# Interactive bash settings shared by login and non-login shells.
export PS1='(\h) \u:\w\$ '
alias ls='ls --color'
# Load bash-completion without re-running every /etc/profile.d snippet:
# several of them append to PATH and are not all idempotent.
if [ -r /etc/profile.d/bash_completion.sh ]; then
    . /etc/profile.d/bash_completion.sh
fi
# login(1) starts a non-root session with /etc/login.defs ENV_PATH, which
# omits the sbin directories; display managers and containers can pass an
# equally reduced PATH, and terminals inherit it.  Put the administrative
# directories back so useradd, mount, iptables and friends resolve.  Keep the
# guard: this file is reached through more than one startup path.
missing=
for d in /usr/local/sbin /usr/sbin /sbin; do
    case ":$PATH:" in
        *":$d:"*) ;;
        *) missing="$missing:$d" ;;
    esac
done
if [ -n "$missing" ]; then
    PATH="${missing#:}:$PATH"
fi
unset d missing
# User-local executables.  Keep the guard: this file is reached through more
# than one startup path.
case ":$PATH:" in
    *:$HOME/.local/bin:*) ;;
    *) PATH="$HOME/.local/bin:$PATH" ;;
esac
export PATH
EOF2
cat > %{buildroot}/etc/profile <<'EOF2'
# Bash login shells share the interactive defaults with display-manager
# terminals through /etc/bashrc.
if [ -n "${BASH_VERSION-}" ] && [ -r /etc/bashrc ]; then
    . /etc/bashrc
fi
for f in /etc/profile.d/*.sh; do
    [ -r "$f" ] && . "$f"
done
unset f
EOF2

# New-user shell startup.  Login shells read /etc/profile (and therefore
# /etc/profile.d) on their own; terminal emulators start interactive
# non-login shells, which only read ~/.bashrc.  Load the system defaults
# there so a new account starts with the same prompt, aliases and
# bash-completion as a login shell.
cat > %{buildroot}/etc/skel/.bash_profile <<'EOF2'
# Login shells already read /etc/profile, which loads the profile.d snippets;
# this file only has to bring in the user's interactive settings.
if [ -r "$HOME/.bashrc" ]; then
    . "$HOME/.bashrc"
fi
EOF2
cat > %{buildroot}/etc/skel/.bashrc <<'EOF2'
# Interactive (non-login) shells, such as the ones terminal emulators start,
# do not read /etc/profile.  Load the same system defaults a login shell gets.
if [ -r /etc/bashrc ]; then
    . /etc/bashrc
fi
EOF2
chmod 644 %{buildroot}/etc/bashrc
chmod 644 %{buildroot}/etc/skel/.bash_profile %{buildroot}/etc/skel/.bashrc

%files
%config(noreplace) /etc/bashrc
%dir /etc/skel
%config(noreplace) /etc/skel/.bash_profile
%config(noreplace) /etc/skel/.bashrc
%config(noreplace) /etc/fstab
%config(noreplace) /etc/systemd/system/default.target
%config(noreplace) /etc/systemd/system/getty.target.wants/serial-getty@ttyS0.service
%config(noreplace) /etc/systemd/journald.conf.d/10-tenko.conf
%dir /etc/systemd/journald.conf.d
%dir /etc/dracut.conf.d
%config(noreplace) /etc/dracut.conf.d/10-tenko.conf
%config(noreplace) /etc/systemd/network/10-dhcp.network
%config(noreplace) /etc/hosts
%dir /etc/polkit-1
%dir /etc/polkit-1/rules.d
%config(noreplace) /etc/polkit-1/rules.d/50-tenko-wheel.rules
%config(noreplace) /etc/shells
%config(noreplace) /etc/inputrc
%config(noreplace) /etc/vimrc
%config(noreplace) /etc/subuid
%config(noreplace) /etc/subgid
%config(noreplace) /etc/profile
%config(noreplace) /etc/locale.conf
%config(noreplace) /etc/vconsole.conf
%config(noreplace) /etc/resolv.conf
%config(noreplace) /etc/machine-id

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-7
- Put /usr/local/sbin, /usr/sbin and /sbin back on PATH in /etc/bashrc when
  they are missing.  login(1) starts a non-root session with the
  /etc/login.defs ENV_PATH, which omits them, and /etc/profile did not
  restore them, so admin tools (useradd, mount, iptables, ...) did not
  resolve in the console session or in the terminals started from it.
  /etc/profile sources /etc/bashrc, so login shells pick the change up at
  the next login; the update is idempotent and keeps any PATH the caller
  already provided.  Accounts whose own ~/.bashrc does not source
  /etc/bashrc need that source line to get the same PATH in interactive
  non-login shells.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-6
- Ship /etc/bashrc with the system prompt, ls alias, bash-completion and
  ~/.local/bin PATH, and load it from /etc/profile and /etc/skel/.bashrc.
  ~/.bashrc previously loaded completion but never set PS1, so a terminal
  started by the desktop fell back to bash's default "bash-5.3$" prompt
  instead of the system prompt login shells already had.  Existing accounts
  keep their own ~/.bashrc; add "if [ -r /etc/bashrc ]; then . /etc/bashrc;
  fi" there (or copy the fresh /etc/skel/.bashrc) to get the same prompt.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-5
- Create /etc/polkit-1/rules.d with mode 0750 to match polkit's directory
  ownership; 0755 made a file conflict in a transaction that installed both
  packages (issue #40).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-4
- Ship /etc/polkit-1/rules.d/50-tenko-wheel.rules so the installer-created
  admin account (wheel) is a polkit administrator for auth_admin actions;
  root stays locked and accountsservice's adm rule remains in place
  (issue #40).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-3
- Add ~/.local/bin to PATH in /etc/profile and /etc/skel/.bashrc.  The
  update is idempotent and covers both login shells and the interactive
  non-login shells started by terminal emulators (issue #34).  /etc/profile
  reaches existing accounts immediately; accounts created before this
  package keep their own ~/.bashrc, so they need the same case block added
  there (or a fresh copy of /etc/skel/.bashrc).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-2
- Ship /etc/skel/.bash_profile and /etc/skel/.bashrc.  Login shells
  already read /etc/profile and its profile.d snippets, but terminal
  emulators start interactive non-login shells that only read ~/.bashrc,
  so a new account had no bash-completion until it sourced the snippet by
  hand.  ~/.bashrc now loads bash_completion.sh without re-running the
  rest of /etc/profile.d (several snippets append to PATH).

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-1
- Rebase on the Tenko 6 distro release with Epoch 1 so installs carrying
  the old 13.1 EVR upgrade cleanly.
- Drop the browneye-sysconfig Obsoletes/Provides alias and the old
  dracut/journald config cleanup; no Browneye installs remain.

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
- Base configuration for Tenko 13.1
