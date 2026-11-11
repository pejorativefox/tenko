Name:       powertop
Version:    2.16.1
Release:    2
Summary:    Diagnose power consumption and power management issues
License:    GPL-2.0-only AND ISC
URL:        https://github.com/fenrus75/powertop
Source0:    %{name}-%{version}.tar.gz
Source1:    %{name}.service
Prefix:     /usr

Requires:   systemd

BuildRequires: meson
BuildRequires: ninja
BuildRequires: gcc
BuildRequires: ncurses
BuildRequires: libnl
BuildRequires: libtracefs
BuildRequires: pciutils
BuildRequires: gettext
BuildRequires: bash-completion

%description
PowerTOP is a Linux tool that diagnoses issues with power consumption and
power management.  Its interactive terminal interface reports per-process
wakeups, CPU idle and frequency states, device power states, and tunables
that can be changed at runtime.  It can also write HTML, CSV and Markdown
reports from a measurement run.

PowerTOP is not part of the base set; it is packaged as an optional
diagnostic tool.  An upstream powertop.service is included for running
"powertop --auto-tune" at boot; it is not enabled by default because
auto-tuning changes live power settings and overlaps with TuneD.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup --prefix=/usr --buildtype=release -Dnls=true ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
install -Dpm0644 %{_sourcedir}/powertop.service \
    %{buildroot}%{_unitdir}/powertop.service

%post
if [ -x /usr/bin/systemctl ]; then
    systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if [ "$1" -eq 0 ] && [ -x /usr/bin/systemctl ]; then
    systemctl stop powertop.service >/dev/null 2>&1 || :
    systemctl disable powertop.service >/dev/null 2>&1 || :
fi

%postun
if [ -x /usr/bin/systemctl ]; then
    systemctl daemon-reload >/dev/null 2>&1 || :
fi

%files -f %{_sourcedir}/powertop.filelist

%changelog
* Wed Nov 11 2026 browneye <build@browneye.invalid> 2.16.1-2
- Ship the upstream powertop.service.  Its ExecStart follows this distro's
  binary location (/usr/bin/powertop instead of upstream's /usr/sbin).
  The unit is installed but not enabled: enabling it runs
  "powertop --auto-tune" at boot and when sleep.target is reached, which
  changes power settings and overlaps with TuneD.  Enable it explicitly
  with "systemctl enable powertop.service" on machines where that is
  wanted.
- Complete the license expression: src/tuning/iw.c, iw.h and nl80211.h
  are ISC, the rest is GPL-2.0-only.

* Wed Nov 11 2026 browneye <build@browneye.invalid> 2.16.1-1
- New package: PowerTOP 2.16.1 (latest stable upstream).  It is not in
  the base set; it is an optional power diagnostic tool.
- Source: https://github.com/fenrus75/powertop/archive/refs/tags/v2.16.1.tar.gz
  md5 60b1441ee4fabfa8ef9dd68dca289944
  sha256 73d5e96d992ed7f040e17c6c9130deebcf42c38990711840981c7afac6f7832f
- Build against the packaged ncurses, libnl, libtracefs and pciutils;
  libtracefs is a new dependency added with this package.
- Installed files: the powertop binary and man page, the bash completion,
  and the native-language message catalogs.
