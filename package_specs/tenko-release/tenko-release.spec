Name:       tenko-release
Version:    6
Release:    1
# Tenko 6 sorts below the old 13.1 EVR, so the compatibility alias is
# explicit rather than derived from %{version}-%{release} (issue #22).
Obsoletes: browneye-release < 13.1-4
Provides: browneye-release = 13.1-4
Summary:    Tenko Linux release file
License:    MIT
Prefix:     /usr

Provides: system-release
Provides: system-release(6)
# Keep old clients and packages working during the compatibility window.
Provides: system-release(13.1)

%description
Release identification for Tenko Linux 6 (Workstation), stable release.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/lib %{buildroot}/etc
cat > %{buildroot}/usr/lib/os-release <<'OSR'
NAME="Tenko Linux"
ID=tenko
VERSION="6 (Workstation)"
VERSION_ID="6"
PRETTY_NAME="Tenko Linux 6 (Workstation)"
VARIANT="Workstation"
VARIANT_ID=workstation
RELEASE_TYPE=stable
ANSI_COLOR="0;34"
OSR
ln -sf ../usr/lib/os-release %{buildroot}/etc/os-release

mkdir -p %{buildroot}/etc/yum.repos.d
cat > %{buildroot}/etc/yum.repos.d/tenko-6.repo <<'REPO'
[tenko-6]
name=Tenko Linux 6 (Workstation)
baseurl=https://repo.pjfox.xyz/tenko/packages/6/
enabled=1
gpgcheck=0
repo_gpgcheck=0
skip_if_unavailable=1
REPO

%posttrans
# Disable the old dnf repository file; keep it as .disabled for rollback.
for f in /etc/yum.repos.d/browneye-13.1.repo \
         /etc/yum.repos.d/browneye-local.repo; do
    if [ -e "$f" ]; then
        mv -f "$f" "$f.disabled"
    fi
done

# Remove old dracut/journald configuration files.  These are
# %%config(noreplace) in the old packages and can survive the obsolete.
rm -f /etc/dracut.conf.d/10-browneye.conf
rm -f /etc/systemd/journald.conf.d/10-browneye.conf

# Remove old units, presets and dracut integration.
rm -f /usr/lib/systemd/system/browneye-firstboot-root-password.service
rm -f /usr/lib/systemd/system/browneye-installer.service
rm -f /usr/lib/systemd/system-preset/90-browneye-firstboot.preset
rm -f /usr/lib/systemd/system-preset/90-browneye-live.preset
rm -f /usr/lib/dracut/dracut.conf.d/20-browneye-live.conf
rm -f /etc/systemd/system/*.wants/browneye-*

# Remove the old RPM macro tree.
rm -f /usr/lib/rpm/macros.d/macros.browneye
rm -rf /usr/lib/rpm/browneye

# Remove old installer payload.
rm -f /usr/bin/browneye-installer
rm -rf /usr/lib/browneye-installer /usr/share/doc/browneye-installer

# Migrate the first-boot marker so the prompt is not repeated.
if [ -e /var/lib/browneye/firstboot-root-password.done ] && \
   [ ! -e /var/lib/tenko/firstboot-root-password.done ]; then
    mkdir -p /var/lib/tenko
    mv -f /var/lib/browneye/firstboot-root-password.done \
        /var/lib/tenko/firstboot-root-password.done
fi
if [ -d /var/log/browneye-install ] && [ ! -d /var/log/tenko-install ]; then
    mv /var/log/browneye-install /var/log/tenko-install
fi

# Remove old package-owned markers and empty runtime directories.
rm -rf /var/lib/browneye/repo
rm -f /usr/share/browneye/base /usr/share/browneye/base-build \
      /usr/share/browneye/base-runtime /usr/share/browneye/workstation \
      /usr/share/browneye/xfce-desktop \
      /usr/share/browneye/xfce-desktop-core \
      /usr/share/browneye/xfce-desktop-full \
      /usr/share/browneye/xfce-desktop-hardware
rmdir /usr/share/browneye /var/lib/browneye /run/browneye 2>/dev/null || true

# Only remove old boot entries once a new tenko entry exists, so an upgrade
# that does not include the kernel package cannot leave the system unbootable.
if [ -d /boot/loader/entries ] && \
   ls /boot/loader/entries/tenko-*.conf >/dev/null 2>&1; then
    rm -f /boot/loader/entries/browneye-*.conf
    if [ -f /boot/loader/loader.conf ]; then
        sed -i 's/^default browneye-/default tenko-/' \
            /boot/loader/loader.conf || true
    fi
fi

%files
/etc/os-release
/usr/lib/os-release
%config(noreplace) /etc/yum.repos.d/tenko-6.repo

%changelog
* Fri Nov 06 2026 tenko <build@tenko.invalid> 6-1
- Adopt the Tenko 6 distro identity: Tenko Linux 6 (Workstation), stable
  release type.  Package versions roll independently; the other renamed
  packages keep their 13.1 (and basefs 1.0) EVRs.
- Keep the browneye-release compatibility alias explicit: 6 sorts below
  13.1, so Obsoletes browneye-release < 13.1-4 and Provides
  browneye-release = 13.1-4 replace the macro-derived alias.
- Ship the tenko-6 repository file and provide system-release(6) plus
  system-release(13.1) for the compatibility window.  The old
  browneye-13.1.repo is disabled by %posttrans.

* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-4
- Rename browneye-release to tenko-release and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-3
- Point the shipped dnf repository at https://repo.pjfox.xyz/packages/13.1/.
  The public tree moved to Cloudflare R2, but the release package still
  installed a browneye-13.1.repo that referenced the retired
  tomfool.8bit.ca host.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-2
- Ship /etc/yum.repos.d/browneye-13.1.repo so an installed system can
  dnf install packages from the published repository

* Fri Oct 30 2026 browneye <build@browneye.invalid> 13.1
- LFS r13.1 release
