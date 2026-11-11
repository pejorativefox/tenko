Name:       tenko-suspend-log
Version:    6
Release:    1
Summary:    Suspend/resume instrumentation for Tenko
License:    MIT
URL:        https://pjfox.xyz/git/daspork/tenko
Prefix:     /usr

Requires:   systemd
Requires:   bash
Requires:   util-linux
Requires:   gawk
Requires:   coreutils
Requires:   grep
Requires:   sed
Requires:   tar
Requires:   gzip

%description
Records every suspend/resume cycle so a failed wake can be diagnosed:

- a systemd-sleep hook logs the power, lid, wakeup-source and suspend_stats
  state before suspend and after resume, including the wakeup device that
  fired and the suspend_stats deltas;
- tenko-resume-probe.service checks the X session, DPMS and backlight a few
  seconds after resume, which separates "kernel resumed, screen stayed
  black" from a real hang;
- tenko-suspend-check.service warns at boot when the previous cycle started
  but never reached userspace;
- tenko-suspend-report collects the whole picture into one tarball for a bug
  report.

Touching /etc/tenko/suspend-debug arms kernel PM debug messages for the next
cycle only.

%prep

%build

%install
rm -rf %{buildroot}
install -Dpm0755 %{_sourcedir}/50-tenko-suspend-log \
    %{buildroot}/usr/lib/systemd/system-sleep/50-tenko-suspend-log
install -Dpm0755 %{_sourcedir}/tenko-resume-probe \
    %{buildroot}/usr/libexec/tenko/tenko-resume-probe
install -Dpm0755 %{_sourcedir}/tenko-suspend-check \
    %{buildroot}/usr/libexec/tenko/tenko-suspend-check
install -Dpm0755 %{_sourcedir}/tenko-suspend-report \
    %{buildroot}/%{_bindir}/tenko-suspend-report
install -Dpm0644 %{_sourcedir}/tenko-suspend-check.service \
    %{buildroot}/usr/lib/systemd/system/tenko-suspend-check.service
install -Dpm0644 %{_sourcedir}/tenko-resume-probe.service \
    %{buildroot}/usr/lib/systemd/system/tenko-resume-probe.service
install -Dpm0644 %{_sourcedir}/40-tenko-suspend-log.preset \
    %{buildroot}/usr/lib/systemd/system-preset/40-tenko-suspend-log.preset
install -Dpm0644 %{_sourcedir}/tenko-suspend-report.8 \
    %{buildroot}/%{_mandir}/man8/tenko-suspend-report.8

%post
if [ -x /usr/bin/systemctl ]; then
    systemctl preset tenko-suspend-check.service >/dev/null 2>&1 || :
fi

%postun
if [ -x /usr/bin/systemctl ]; then
    systemctl daemon-reload >/dev/null 2>&1 || :
fi

%files -f %{_sourcedir}/tenko-suspend-log.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 6-1
- New package: instrument suspend/resume so a failed wake can be debugged.
  The first lid-suspend test on the ThinkPad suspended correctly but did
  not bring the desktop back on the first resume, and the journal showed
  only that the kernel had resumed: there was no record of the wakeup
  source, backlight/DPMS state, AC/battery, lid state or of a resume that
  never reached userspace.  The sleep hook, the post-resume X probe, the
  boot-time incomplete-cycle check and tenko-suspend-report cover those
  gaps; /etc/tenko/suspend-debug additionally enables the kernel PM debug
  messages for one cycle.  No behaviour change unless the debug flag is
  present.
