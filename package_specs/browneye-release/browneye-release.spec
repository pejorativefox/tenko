Name:       browneye-release
Version:    13.1
Release:    1
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

%files
/etc/os-release
/usr/lib/os-release

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 13.1
- LFS r13.1 release
