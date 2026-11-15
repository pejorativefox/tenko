Name:       auto-cpufreq
Version:    3.2.0
Release:    1
Summary:    Automatic CPU speed and power optimizer for Linux
License:    GPL-3.0-or-later
URL:        https://github.com/AdnanHodzic/auto-cpufreq
Source0:    %{name}-%{version}.tar.gz
Source1:    %{name}.service
# Packaged layout: plain poetry-core backend, no GTK GUI, requests only for
# the source-install self-updater, files under /usr and /var/lib, and
# --install/--remove enable or disable the packaged systemd unit.
Patch0:     %{name}-%{version}-tenko.patch
Prefix:     /usr
BuildArch:  noarch

BuildRequires: python3-poetry-core
Requires:   coreutils
Requires:   dmidecode
Requires:   grep
Requires:   kmod
Requires:   python3-click
Requires:   python3-distro
Requires:   python3-psutil
Requires:   python3-pyasyncore
Requires:   python3-pyinotify
Requires:   python3-urwid
Requires:   systemd

%description
auto-cpufreq monitors battery state, CPU usage, temperature and system load
and switches the CPU governor, frequency limits and turbo boost to balance
performance and battery life.  The daemon is not enabled on installation:
run "sudo auto-cpufreq --install" (or enable auto-cpufreq.service), which
also stops TuneD and power-profiles-daemon.  Settings are read from
/etc/auto-cpufreq.conf; an example is in the documentation directory.

%prep
%setup -q
%patch -P 0 -p1

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi
install -Dm755 scripts/cpufreqctl.sh %{buildroot}%{_bindir}/cpufreqctl.auto-cpufreq
install -Dm644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/%{name}.service
install -Dm644 auto-cpufreq.conf-example %{buildroot}%{_docdir}/%{name}/auto-cpufreq.conf-example
install -Dm644 README.md %{buildroot}%{_docdir}/%{name}/README.md
install -dm755 %{buildroot}/var/lib/%{name}

%files -f %{_sourcedir}/%{name}.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 3.2.0-1
- New package, not in the base set: latest upstream stable release
  (3.2.0, checked 2026-11-15).  CLI and daemon only (no GTK GUI); the
  self-updater's requests import is made lazy so requests is not needed.
