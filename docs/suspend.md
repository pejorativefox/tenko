# Suspend and resume

Lid policy belongs to `systemd-logind`, not the desktop.  `tenko-sysconfig`
ships `/etc/systemd/logind.conf.d/10-lid-switch.conf`:

```ini
[Login]
HandleLidSwitch=suspend
HandleLidSwitchExternalPower=suspend
HandleLidSwitchDocked=ignore
```

The XFCE power manager is built with `logind-handle-lid-switch` defaulting to
TRUE (patch in `package_specs/xfce4-power-manager/files/`), so it does not
claim `handle-lid-switch` with a block inhibitor.  A desktop that does claim
it makes logind ignore the lid entirely; this way XFCE, a bare window manager
and a console-only system all follow the same policy.  A user can opt back
into the XFCE lid action with:

```sh
xfconf-query -c xfce4-power-manager \
    -p /xfce4-power-manager/logind-handle-lid-switch -n -t bool -s false
```

Logind treats only a real dock as docked, not an external monitor, so closing
the lid with a monitor attached suspends.

## Instrumentation

`tenko-suspend-log` records each cycle under the `tenko-suspend` journal tag:

| line | written by | meaning |
| --- | --- | --- |
| `action=start` | `/usr/lib/systemd/system-sleep/50-tenko-suspend-log` | before suspend: uptime, AC/battery, lid, `mem_sleep`, `wakeup_count`, backlight, enabled wakeup devices, `suspend_stats` snapshot |
| `action=resume` | same hook, post phase | kernel and userspace are back: elapsed time, wakeup IRQ, wakeup sources whose counters rose, `suspend_stats` deltas, backlight and lid |
| `action=probe` | `tenko-resume-probe.service` | a few seconds later: X session answered, monitor/DPMS state, backlight.  This is the completion marker |

`tenko-suspend-check.service` runs at boot and warns when the previous boot
has an `action=start` without a matching `action=probe` (hard hang, failed
userspace resume or power loss).  The warning names the cycle id and points
at `journalctl -b -1 -t tenko-suspend`.

`efi_pstore` and `systemd-pstore.service` are enabled; kernel dumps are
archived under `/var/lib/systemd/pstore/`.  They are the only evidence for a
resume that wedges before journald can write, so check that directory when
the journal simply stops.

### Debugging one cycle

```sh
sudo mkdir -p /etc/tenko && sudo touch /etc/tenko/suspend-debug
# close/open the lid once
sudo tenko-suspend-report
```

With the flag present the next cycle sets `/sys/power/pm_debug_messages=1`
and `/sys/power/pm_print_times=1` (verbose per-device PM messages in dmesg),
and the resume probe turns the display back on when it detects it is off.
Both are restored afterwards.  Remove the file when done:

```sh
sudo rm /etc/tenko/suspend-debug
```

### Reporting

```sh
sudo tenko-suspend-report [output.tar.gz]
```

The tarball contains the current and previous boot journals (filtered to PM,
ACPI, GPU, input, logind, LightDM, XFCE and `tenko-suspend` lines),
`suspend_stats`, wakeup sources, the Xorg log, dmesg, session/X/DPMS state,
BIOS/EC and firmware versions and the pstore listing.  Attach it to a
GitHub issue.  Journal excerpts can contain Wi-Fi names.
