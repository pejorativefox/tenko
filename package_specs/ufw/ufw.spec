Name:       ufw
Version:    0.36.2
Release:    1
Summary:    Uncomplicated Firewall command-line interface for netfilter
License:    GPL-3.0-only
URL:        https://launchpad.net/ufw
Source0:    %{name}-%{version}.tar.gz
Source1:    ufw.service
Source2:    README.Tenko
# Use setuptools' distutils on Python 3.15 and keep the upstream unit tests
# compatible with the current unittest API.
Patch0:     %{name}-%{version}-python.patch
Prefix:     /usr
BuildArch:  noarch

BuildRequires: iptables
BuildRequires: iana-etc
BuildRequires: procps-ng
BuildRequires: python-setuptools
Requires:   coreutils
Requires:   grep
Requires:   iana-etc
Requires:   iptables
Requires:   kmod
Requires:   procps-ng
Requires:   systemd

%description
UFW provides an easy-to-use command-line interface for managing IPv4 and
IPv6 netfilter rules with iptables. It supports application profiles,
connection rate limiting, logging and routed traffic rules.

The firewall and its boot service are disabled on installation. Allow
remote administration traffic before running "ufw enable", and enable
ufw.service to restore the configured firewall at boot. See README.Tenko.

%prep
%setup -q
%patch -P 0 -p1
# Tenko uses merged /usr; helpers are read-only code, not /lib state.
sed -i "s@os.path.join('/lib', 'ufw')@os.path.join('/usr/lib', 'ufw')@" setup.py
sed -i 's@ufw/lib/ufw@ufw/usr/lib/ufw@' tests/unit/support.py

%build
make mo
python3 setup.py build

%install
rm -rf %{buildroot}
python3 setup.py install --root=%{buildroot} --prefix=/usr \
    --install-lib=%{_libdir}/python3.15/site-packages \
    --single-version-externally-managed --record=installed-files.txt
install -dm755 %{buildroot}%{_bindir}
mv %{buildroot}/usr/sbin/ufw %{buildroot}%{_bindir}/ufw
sed -i '1c#!/usr/bin/python3' %{buildroot}%{_bindir}/ufw
install -Dm644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/ufw.service
install -Dm644 shell-completion/bash \
    %{buildroot}/usr/share/bash-completion/completions/ufw
install -Dm644 README %{buildroot}%{_docdir}/ufw/README
install -Dm644 %{SOURCE2} %{buildroot}%{_docdir}/ufw/README.Tenko
install -Dm644 COPYING %{buildroot}%{_datadir}/licenses/ufw/COPYING
# Fail the build rather than silently shipping an active firewall, losing IPv6
# coverage or disabling the root/configuration integrity checks.
grep -qx 'ENABLED=no' %{buildroot}/etc/ufw/ufw.conf
grep -qx 'IPV6=yes' %{buildroot}/etc/default/ufw
grep -qx 'do_checks = True' \
    %{buildroot}%{_libdir}/python3.15/site-packages/ufw/common.py

%check
# Only the upstream unit suite: fake iptables and a temporary config tree.
# Root/root_kern tests must not modify the builder's host-network firewall.
python3 tests/unit/runner.py

%files -f %{_sourcedir}/ufw.filelist

%changelog
* Wed Nov 25 2026 tenko <build@tenko.invalid> 0.36.2-1
- New optional package, not in the base set: latest upstream stable
  release (0.36.2, checked 2026-11-25).
- Include IPv4/IPv6 rules, application profiles, translations, shell
  completion and an opt-in systemd service; preserve local configuration.
- Adapt the build and unit tests for Python 3.15 and install helpers under
  /usr/lib/ufw without enabling or changing the host firewall.
