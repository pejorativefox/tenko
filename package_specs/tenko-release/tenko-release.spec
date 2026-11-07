Name:       tenko-release
Version:    6
Release:    2
Summary:    Tenko Linux release file
License:    MIT
Prefix:     /usr

Provides: system-release
Provides: system-release(6)

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
baseurl=https://tenko.pjfox.xyz/packages/6/
enabled=1
gpgcheck=0
repo_gpgcheck=0
skip_if_unavailable=1
REPO

%files
/etc/os-release
/usr/lib/os-release
%config(noreplace) /etc/yum.repos.d/tenko-6.repo

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-2
- Drop the browneye-release Obsoletes/Provides alias, the
  system-release(13.1) provide and the old-tree %posttrans cleanup; no
  Browneye installs remain.

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
- Tenko 13.1 release
