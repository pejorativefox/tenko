Name:       browneye-release
Version:    13.1
Release:    2
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
baseurl=https://tomfool.8bit.ca/browneye/packages/13.1/
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
* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-2
- Ship /etc/yum.repos.d/browneye-13.1.repo so an installed system can
  dnf install packages from the published repository

* Fri Oct 30 2026 browneye <build@browneye.invalid> 13.1
- LFS r13.1 release
