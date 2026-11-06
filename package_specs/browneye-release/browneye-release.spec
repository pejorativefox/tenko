Name:       browneye-release
Version:    13.1
Release:    3
Summary:    Browneye Linux release file
License:    MIT
Prefix:     /usr

Provides: system-release
Provides: system-release(%{version})

%description
Release identification for Browneye Linux 13.1.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/lib %{buildroot}/etc
cat > %{buildroot}/usr/lib/os-release <<'OSR'
NAME="Browneye Linux"
ID=browneye
VERSION="13.1"
VERSION_ID="13.1"
PRETTY_NAME="Browneye Linux 13.1"
ANSI_COLOR="0;34"
OSR
ln -sf ../usr/lib/os-release %{buildroot}/etc/os-release

mkdir -p %{buildroot}/etc/yum.repos.d
cat > %{buildroot}/etc/yum.repos.d/browneye-13.1.repo <<'REPO'
[browneye-13.1]
name=Browneye Linux 13.1
baseurl=https://repo.pjfox.xyz/packages/13.1/
enabled=1
gpgcheck=0
repo_gpgcheck=0
skip_if_unavailable=1
REPO

%files
/etc/os-release
/usr/lib/os-release
%config(noreplace) /etc/yum.repos.d/browneye-13.1.repo

%changelog
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
