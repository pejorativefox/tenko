# Installer UX review and modernization proposal

Status: proposal, partially implemented.

Implemented so far:

* guided flow: erase disk / use free space / custom, filesystem and swap
  choices, review page, a single confirmation for create-only plans and the
  typed ERASE confirmation when existing partitions are deleted;
* proportional disk map with ESP/Windows/Linux/free labels in the disk
  picker, guided method screen and layout editor;
* direct partition actions in the advanced editor (Enter on a partition row
  opens assign/delete/keep; no typed partition numbers);
* GiB-based size inputs (`20`, `20G`, `20GiB`, `512M`);
* swapfile default (guided and advanced), with a swap partition still
  available;
* optional colour in the ncurses UI (`NO_COLOR` disables it).

Still open: encryption, btrfs subvolumes, timezone/keymap/locale, existing-OS
labels, "install alongside" (shrink), answer-file v3, plain-mode parity and
the optional graphical front end.

Scope: the interactive experience of `tenko-installer` (the ncurses
installer on the live ISO).  The install backend, the answer-file format and
the ISO build are only covered where the UX depends on them.

## TL;DR

The backend is in good shape: a pure partition planner, snapshot/verify/
rollback, `--dry-run`, `--plan-json` and `--simulate` are better foundations
than most small distributions have.  The problem is the **flow**: the
installer drops every user into a manual partition editor, even when they
just want to erase one disk and install.

The single biggest improvement is therefore not a different toolkit.  It is
to make **"erase this disk and install" the default path** and keep the
current editor as an explicit *Advanced* option.

Recommended direction:

1. Guided-first TUI: 4 screens after the welcome (disk, account, review,
   install), no partition numbers, no MiB fields.
2. Redesign the advanced editor around a visual disk map and direct row
   actions instead of a menu of "type the partition number" forms.
3. Add the modern defaults users expect: swapfile instead of a swap
   partition, optional LUKS2, ext4 or btrfs, timezone and keyboard layout.
4. Keep the TUI for now.  A GTK/web front end is a separate project with a
   real dependency and ISO-size cost; it should reuse the same backend, not
   replace it.

## 1. What the installer does today

### 1.1 Flow

```
preflight message
  -> select disks (toggle checkboxes; "topmost" selected disk is root)
  -> for each selected disk: partition editor (pre-filled with ESP+swap+root)
  -> package set (desktop / base)
  -> hostname + admin + password
  -> type root disk path and ERASE
  -> install progress
```

Code map:

| Area | File / function |
| --- | --- |
| Disk selection | `main.py:_select_disks` |
| Default layout for the root disk | `main.py:_default_disk_spec` |
| Partition editor | `main.py:_edit_disk` |
| Create-partition form | `main.py:_add_partition_form` |
| Adopt-existing form | `main.py:_assign_existing_form` |
| Plain/serial flow | `main.py:run_plain` |
| Confirmation | `main.py:_confirm_lines`, `main.py:_interactive` |
| TUI toolkit | `ui.py` |
| Planner | `layout.py`, `disk.py` |

### 1.2 Concrete pain points

These are the things a first-time user hits, in order.

1. **There is no guided install.**  Selecting a disk immediately opens the
   partition editor.  A user who wants "use the whole disk" still has to
   understand ESP, swap, root, roles and sizes before they can press Done.

2. **Pressing Enter on an existing partition does nothing.**  In
   `_edit_disk`, the menu contains existing partitions, planned partitions
   and then action rows.  Only the action rows are handled (`action =
   choice - actions`); `choice` for a partition row yields a negative action
   and the loop silently redraws.  The only way to touch a partition is to
   scroll to "Toggle delete..." or "Assign an existing partition..." and
   type its number.

3. **Partition numbers are typed by hand.**  `_assign_existing_form` and the
   delete action ask for "Partition number"; the partition is already
   visible on screen.  This is error-prone and feels like a 1990s tool.

4. **Sizes are raw MiB.**  "Size MiB (blank = fill region)" and "Region
   start MiB (blank = auto)" expose the planner's internal units.  There is
   no `20 GiB`, no `50%`, no "use the remaining space" default in the form.

5. **Forms discard input on validation failure.**  `_add_partition_form`
   returns `None` after showing the error; the caller simply returns to the
   menu, so the user has to reopen the form and retype everything.

6. **The default layout is invisible.**  The root disk is pre-seeded with
   ESP + 2 GiB swap + ext4 root, but the editor shows these as "NEW esp",
   "NEW swap", "NEW root" rows mixed with existing entries.  There is no
   "this is what will be created" summary and no disk map.

7. **The root disk is implicit and the wording is misleading.**  The disk
   screen says "the topmost selected disk becomes the root disk", but
   `chosen` is built in probe order, not in the order the user toggled the
   disks.  With two selected disks, which one gets `/` is not obvious.

8. **Every selected disk gets an editor.**  Adding `/home` on a second disk
   means going through a full "Done with this disk" cycle for it too.
   Multi-disk works, but it feels like a sequence of unrelated editors.

9. **Swap is always a partition.**  `_default_disk_spec` adds a 2 GiB swap
   partition.  Modern desktop installs normally use a swapfile or zram;
   a swap partition is an extra decision (and an extra partition) that most
   users do not need.

10. **No encryption option.**  `layout.py` knows the LUKS GPT type name but
    there is no LUKS support in the planner or installer.  Encryption is a
    standard expectation on laptops in 2026.

11. **No timezone, locale or keyboard layout.**  The account form asks for
    hostname, user and password only.  `install.py` never writes
    `/etc/localtime`, `/etc/locale.conf` or `/etc/vconsole.conf`, so the
    installed system keeps the live environment's defaults.  For a desktop
    distribution this is a visible gap.

12. **No existing-OS awareness.**  Partitions are labelled with type names
    and filesystem names, not "Windows 11" or "existing Tenko".  There is
    no warning that the selected ESP belongs to another OS.

13. **Back navigation loses work.**  The wizard is a sequence of function
    calls; "Back" from package/account goes to the disk editor, and
    cancelling the confirmation recursively calls `_interactive` again
    (`main.py`, around `typed is None`).  There is no step list or summary
    page from which a single choice can be changed.

14. **The confirmation is high-friction for the common case.**  Typing the
    disk path and `ERASE` is appropriate for a custom destructive layout,
    but it is overkill for "erase this blank disk".  At the same time the
    review page is a flat text list, so it is not obvious which partitions
    will be deleted versus kept.

15. **The TUI is deliberately minimal.**  No color, no mouse, no Unicode,
    no table widget, no toggles, no scrollable help.  `ui.py` supports
    menus, text fields, a typed confirmation and a log pane.  That is enough
    for the current flow but not for a modern guided experience.

### 1.3 What is already good and should be preserved

* The pure planner and its tests.  UI work should call planner functions,
  never emit partition commands directly.
* Snapshot + verify + rollback of untouched partitions.  This is a genuine
  safety differentiator and should stay invisible but active.
* `--simulate` with synthetic disks.  It makes UX development and
  regression testing possible without root.
* The answer file and `--plan-json` / `--dry-run`.  Automation is already
  first-class; the UI should simply edit the same model.
* The plain/serial fallback.  Keep it, but make it use the guided flow too.
* The separation between `probe` (read), `layout` (plan) and `install`
  (execute).  Do not collapse it for UI convenience.

## 2. What other distributions do in 2026

| Installer | UI | Storage model | Notable ideas |
| --- | --- | --- | --- |
| Fedora Anaconda Web UI (F42+) | Web UI in a local browser/kiosk | Guided goals + Cockpit Storage for manual | Short linear flow: welcome, installation method, storage, review.  Goal-based guided partitioning (erase, free space, reinstall, preserve `/home`). |
| Ubuntu 26.04 desktop | Flutter GUI | Erase disk / install alongside / manual | Separate encryption step (passphrase or hardware-backed/TPM).  A review page lists disk, encryption, apps and partitions before installing. |
| openSUSE Agama (18-24) | Web UI | Guided + expert; JSON profiles | Storage page was explicitly redesigned for clarity in Agama 18.  JSON profiles can be validated offline.  Expert partitioning is still the weak spot. |
| Calamares (many distros) | Qt GUI | Erase disk / install alongside / replace partition / manual | Four explicit storage choices on one screen.  Encryption checkbox on erase/alongside.  Manual mode is a real partition table (kpmcore). |
| archinstall 3.x | TUI | Best-effort default / manual / pre-mounted | Guided vs advanced.  btrfs subvolumes + snapshot type.  Encryption lives in the disk menu.  JSON config for automation. |
| Debian installer | newt TUI | Guided schemes + partman | Guided "all files in one partition", "separate /home", "encrypted LVM"; manual partitioning as a separate path. |
| NixOS | Calamares or declarative CLI | Declarative config | The installer is a thin front end over a configuration; unattended installs are the norm. |

### 2.1 Patterns worth copying

1. **Guided first, advanced on demand.**  Every mainstream desktop installer
   offers a one-click automatic layout and hides the partition table behind
   an "Advanced/Custom" choice.  None of them start in a partition editor.
2. **Goal-oriented storage choices, not device-oriented ones.**  Users pick
   "erase this disk", "install alongside", "replace a partition" or
   "manual"; they do not pick "edit `/dev/nvme0n1`" first.
3. **A visual disk map.**  A proportional bar with existing partitions,
   free space, and labels such as "Windows" makes the consequence obvious
   without reading a table.
4. **A review page.**  Storage, encryption, account, packages and boot
   loader are shown together before the first destructive command.
5. **Encryption is a first-class, simple option.**  A checkbox or a dedicated
   step; Ubuntu now also offers hardware-backed (TPM) unlock.
6. **Declarative profiles are part of the product.**  Agama JSON,
   archinstall JSON, Ubuntu autoinstall.  The GUI is one editor of the same
   document that automation uses.
7. **Modern automatic layouts avoid swap partitions.**  Fedora Workstation
   uses zram; Ubuntu uses a swapfile.  A fixed swap partition is a server
   convention, not a desktop default.
8. **The web UI is a real trend, but not free.**  Anaconda and Agama ship a
   browser-sized stack.  Distributions with a console-only live image
   (Alpine, Void, Debian netinst) still use a TUI, and that is not
   inherently worse UX; the flow matters more than the renderer.

### 2.2 Patterns to avoid

* **Anaconda's Cockpit Storage integration** is powerful but heavy, and its
  manual storage flow has been criticised as a regression for newcomers.
  Tenko does not need a general-purpose storage manager inside the
  installer.
* **Agama's expert partitioning** is still catching up.  A guided flow plus
  a focused editor is a better target than a full disk-management suite.
* **Calamares' ordering trap.**  Users have selected "Erase disk" and then
  "Manual partitioning", expecting the first choice to pre-clear the disk.
  The choices must be mutually exclusive and the review must show the
  actual result.
* **A destructive default that is pre-selected.**  "Erase disk" should be an
  explicit choice even when it is the recommended one.

## 3. Recommended UX

### 3.1 Principles

* **The common case must not require partitioning.**  One disk, one
  filesystem, one account, install.
* **Destructive actions are visible.**  The review page shows exactly what
  will be deleted, created, formatted and kept.
* **No internal units in the UI.**  Sizes are shown in GiB with a unit
  selector; partition numbers and region offsets never appear as input.
* **Direct manipulation.**  Selecting a row acts on that row.  Typing a
  number to identify an object that is already highlighted is forbidden.
* **Validation is inline and non-destructive.**  An invalid value keeps the
  form open with the value intact and an error line, instead of closing and
  discarding everything.
* **The UI edits the same model as the answer file.**  A "Save profile"
  action should produce a JSON file that reproduces the install unattended.
* **Graceful degradation.**  Color and mouse are enhancements; the installer
  still works on `TERM=linux` and over serial.

### 3.2 Guided flow

Five screens, of which only three require input:

```
1. Welcome / preflight
   - UEFI, GPT-capable disks, network, repository
   - [ Install Tenko 6 ]   [ Advanced installation ]

2. Where to install
   - disk list (model, size, current contents, free space)
   - installation type: Erase disk / Use free space / Custom
   - optional: encrypt, filesystem, swap mode
   - live consequence summary

3. Account
   - hostname, username, password, confirm
   - timezone, keyboard layout
   - package set (Desktop / Base)

4. Review
   - storage summary grouped by disk (ERASE / CREATE / KEEP)
   - encryption, account, packages, boot loader
   - [ Install ]   [ Back ]

5. Installing
   - step list + progress + log
   - on failure: step, error, remedy, save log
```

#### Screen 2 mock-up

```
 Install Tenko 6
 ┌──────────────────────────────────────────────────────────────────┐
 │ Where should Tenko be installed?                                 │
 │                                                                  │
 │   ( ) /dev/nvme0n1   Samsung 980 PRO 1 TB                        │
 │       [ Windows 400G ][ ESP 100M ][ free 500G ]                  │
 │   (*) /dev/sda       QEMU HARDDISK 20 GB                         │
 │       [              free 20 GB                              ]   │
 │                                                                  │
 │   Installation type                                              │
 │     (*) Erase the disk and install Tenko                         │
 │     ( ) Use the existing free space (keep all partitions)        │
 │     ( ) Custom partitioning...                                   │
 │                                                                  │
 │   Filesystem  [ ext4        v ]    Swap  [ swapfile       v ]    │
 │   [ ] Encrypt the system (passphrase required at boot)           │
 │                                                                  │
 │   This will ERASE /dev/sda (20 GB). No other disk is touched.    │
 └──────────────────────────────────────────────────────────────────┘
   Up/Down move   Enter select/toggle   Tab next   Esc back   q quit
```

Notes:

* The disk bar is proportional.  Free space is rendered distinctly; existing
  OS partitions get a label from the probe (section 4.5).
* "Erase the disk" is the recommended option but is not pre-selected until
  the user chooses a disk.  This avoids click-through destruction.
* "Use existing free space" is the safe dual-boot path when the user has
  already shrunk Windows.  It creates an ESP only if the disk has none, and
  reuses an existing ESP when present.
* "Custom" opens the advanced editor described below, starting from the
  current disk table.
* Encryption and filesystem live on this screen because they are part of
  the same decision.  A separate "Advanced features" page is also fine, but
  do not hide encryption three levels deep.
* Swap mode: `swapfile` (default), `none`, `partition` (advanced, needed for
  hibernation).  zram is a possible future default once a zram-generator
  package is in the repo.

#### Screen 4 mock-up

```
 Review
 ┌──────────────────────────────────────────────────────────────────┐
 │ Storage                                                          │
 │   /dev/sda  20 GB   ERASE ENTIRE DISK                            │
 │     create  /boot   1 GiB   vfat   (EFI System Partition)        │
 │     create  /      19 GiB   ext4   (rest of the disk)            │
 │     swapfile 2 GiB on /                                           │
 │                                                                  │
 │   /dev/nvme0n1  NOT MODIFIED                                     │
 │                                                                  │
 │ Encryption  none                                                 │
 │ Account     admin (wheel), hostname tenko                        │
 │ Packages    Desktop (tenko-base + xfce-desktop)                  │
 │ Boot        systemd-boot on /dev/sda1                            │
 │                                                                  │
 │ Type ERASE to confirm: ______                                    │
 └──────────────────────────────────────────────────────────────────┘
```

Confirmation policy:

* If the plan deletes any existing partition, require the typed word
  `ERASE`.
* If the disk is blank and the plan only creates partitions, a single
  explicit "Install" is enough; the review still lists every operation.
* Never require the disk path as a second phrase; it is redundant with the
  selected disk shown above and adds typing without adding safety.

### 3.3 Advanced storage editor

This replaces `_edit_disk` and the two blind forms.

```
 Storage: /dev/nvme0n1
 ┌──────────────────────────────────────────────────────────────────┐
 │ [ ESP 100M ][ Windows 400G ][ Tenko 80G ][ free 420G ]           │
 │                                                                  │
 │   #  Device        Size    Type       FS     Mount    Action     │
 │   1  nvme0n1p1    100M    EFI        vfat   /boot    keep       │
 │   2  nvme0n1p2    400G    Windows    ntfs   -        keep       │
 │   3  nvme0n1p3     80G    Linux      ext4   /        format     │
 │   4  free          420G   -          -      -        -          │
 │                                                                  │
 │   Enter edit   n new   d delete   f format   a auto layout       │
 │   ? help       r rescan   Esc back                               │
 └──────────────────────────────────────────────────────────────────┘
```

Selecting a row opens an action sheet, not a blind form:

```
 Partition /dev/nvme0n1p3
   Mount point   [ /              v ]   (/, /home, /var, custom, none)
   Filesystem    [ ext4           v ]   (keep, ext4, btrfs, vfat, swap)
   Size          [ 80.0 ] [ GiB v ]  [x] Use the remaining space
   [x] Format this partition
   [ ] Encrypt this partition (LUKS2)
   [ Apply ]   [ Delete partition ]   [ Cancel ]
```

Rules:

* New partitions default to "use the remaining space" and ext4.
* The mount-point list offers `/`, `/home`, `/var`, `/srv`, `swap`, and
  "custom"; typing a custom absolute path is allowed but is not the default
  interaction.
* The filesystem list only contains supported types and explains the
  consequences in a one-line hint ("btrfs: snapshots and subvolumes").
* "Delete partition" is an action on the selected row and requires a
  confirmation naming the partition and its size.  It does not ask the user
  to type a number that is already on screen.
* Free space rows are selectable; selecting one opens "create partition"
  with the region already filled in.  If there are several free regions, the
  row identifies the region by start and size in GiB.
* Errors appear on a dedicated line at the bottom of the sheet; the sheet
  stays open and the values remain.
* The advanced editor is a single global screen for all disks, or a per-disk
  screen with a disk tab bar.  Either is fine; the key is that "add another
  disk" is a deliberate action, not a forced editor for every selected disk.

### 3.4 Multi-disk

* Guided mode installs to one disk.
* Advanced mode starts with that disk and offers "Add disk..." for `/home`,
  `/var`, etc.  The existing planner already supports this; only the flow
  changes.
* The review page groups by disk and marks each disk `MODIFIED` or
  `NOT MODIFIED`.

### 3.5 Account and locale

Add to the account page:

* Timezone (searchable list; default from the live environment if it is
  configured, otherwise UTC).
* Keyboard layout (list from `/usr/share/kbd/keymaps`; default `us`).
* Locale (default `en_US.UTF-8`; a short list of `en_US`, `en_GB`, `de_DE`,
  `fr_FR`, `es_ES`, etc. is enough for the first version).
* Hostname, username, password, confirm (existing).
* Package set (Desktop / Base) stays on this page or moves to the disk page;
  either way it must be visible in the review.

`install.py` gains a `step_locale` (or extends `step_configure`) that writes:

```
/etc/localtime       -> /usr/share/zoneinfo/<zone>
/etc/locale.conf     LANG=<locale>
/etc/vconsole.conf   KEYMAP=<keymap>
```

The answer file gets `timezone`, `locale`, `keymap`.  The live environment
must contain `tzdb` and `kbd`; both packages already exist in
`package_specs/`.

### 3.6 Progress and failure

* Left side: the nine existing steps, with current/complete/failed markers.
* Right side: the last ~15 log lines (the current `ProgressView` already
  does this).
* `L` opens a full-screen scrollable log; `S` saves the log to a selected
  USB stick; `Q` asks before aborting.
* On failure: show the failed step, the error, the remedy and the log path.
  Offer "Save log to USB" and "Reboot".  Do not claim automatic rollback
  after formatting has started; the current `InstallError.reversible` flag
  already knows the difference.
* Show elapsed time and, where possible, a per-step mark rather than a
  fake percentage.  The current bar is step-based, which is honest.

## 4. Backend work

The UI proposal is only credible if the backend supports it.  These are the
pieces, in dependency order.

### 4.1 Guided layout planner

Add pure functions to `layout.py`:

```python
def plan_erase_disk(table, *, fstype="ext4", swap="swapfile",
                    encrypt=False) -> DiskSpec: ...
def plan_free_space(table, *, fstype="ext4", swap="swapfile",
                    encrypt=False) -> DiskSpec: ...
```

They return a `DiskSpec` that the existing `plan_disk` / `InstallLayout`
machinery consumes.  "Erase disk" means `delete_partitions` covers every
existing partition, not just the ones the user marked.  "Free space" means
no deletions and placement in the largest suitable region.

Benefits: unit-testable without curses; the answer file can use the same
functions; the UI becomes a thin editor.

### 4.2 Swapfile instead of a swap partition

* New config field `swap_mode: "none" | "swapfile" | "partition"`.
* Default `swapfile`, size 2 GiB or `min(2 GiB, RAM/4)`; make it a choice,
  not a hidden constant.
* `install.py`: create the file after the root filesystem is mounted
  (`fallocate` or `dd`, `chmod 600`, `mkswap`, `swapon`), add an fstab entry.
  On btrfs, create it with `chattr +C` or use a dedicated subvolume to avoid
  COW.
* Remove the swap partition from `_default_disk_spec` / `_default_root_partitions`.
* Keep `partition` for users who need hibernation; document that hibernation
  is not configured by default.
* Avoid zram until a `zram-generator` package (or an equivalent systemd
  unit) is available in the repo.  A swapfile is simpler and works on both
  ext4 and btrfs.

### 4.3 LUKS2

This is the largest new feature.  It is also the one users will notice.

Data model:

* `PartitionSpec.encrypt: bool` (or a separate `EncryptedVolume` layer).
* The mapper name and the LUKS UUID must be part of the planned partition,
  not guessed at install time.
* The ESP stays unencrypted; `/boot` is the ESP, so the kernel and initramfs
  are unencrypted (which is normal for systemd-boot without a separate
  XBOOTLDR + encrypted `/boot`).

Install steps:

1. `cryptsetup luksFormat --type luks2` on the root (and optionally data)
   partition.
2. `cryptsetup open` it as `cryptroot`.
3. `mkfs` on `/dev/mapper/cryptroot`.
4. Mount and install as usual.
5. Write `/etc/crypttab` with the LUKS UUID.
6. Add `rd.luks.uuid=luks-...` to the kernel command line and ensure
   dracut includes the `crypt` module (the live initramfs already needs
   `dm`; add `crypt`).
7. `systemd-boot` entries reference the same UUID.

Packages: `cryptsetup` exists in `package_specs/`.  Add it to `tenko-live`
and to the target package set when encryption is selected.

Testing: QEMU install with a passphrase, boot and unlock; wrong passphrase;
missing crypttab; resume from suspend is out of scope.

Possible later enhancement: TPM2 enrollment (`systemd-cryptenroll
--tpm2-device=auto`) to match Ubuntu's "hardware-backed encryption".  Do not
make it the default without a recovery-key flow.

### 4.4 Btrfs subvolumes

If btrfs remains a supported root filesystem, make it worth choosing:

* Default subvolumes: `@` → `/`, `@home` → `/home`, `@log` → `/var/log`,
  `@cache` → `/var/cache`, `@snapshots` → `/.snapshots`.
* Mount options: `compress=zstd`, `noatime`, `space_cache=v2`.
* Snapshots (snapper/timeshift) are a separate decision; no snapper package
  exists in the repo today, so do not promise snapshot integration yet.
* The planner needs a subvolume map per partition; mount/fstab generation
  must use `subvol=` options.

If this is too much for the first milestone, keep btrfs as "one filesystem,
no subvolumes" and say so in the UI.  A half-configured btrfs is worse than
ext4.

### 4.5 Existing-OS detection

Extend `probe.py` to annotate partitions for display:

* GPT type GUID (ESP, Microsoft basic data, Linux filesystem, Linux LUKS,
  Windows recovery).
* Filesystem label and UUID.
* For an ESP, mount it read-only and look for `EFI/Microsoft/Boot/bootmgfw.efi`,
  `EFI/<distro>/`, `loader/entries/`.
* Machine-readable output stays in `ProbedDisk`; the UI decides how to
  label it.

This is display-only in the first version.  It supports "Windows is on this
disk" warnings and makes the disk map meaningful.  Actual "install
alongside" also needs shrink support (see 4.6).

### 4.6 Alongside / shrink (defer)

"Install alongside Windows" is the most requested dual-boot flow, but it is
also the most dangerous:

* Needs `ntfsresize` (ntfs-3g), `resize2fs`, `btrfs filesystem resize`.
* Must refuse BitLocker-encrypted volumes.
* Must handle the Windows ESP (usually 100 MiB) and the need for a larger
  ESP or XBOOTLDR.
* Must verify free space after the shrink and keep a rollback path.

Recommendation: ship "Use existing free space" first.  It covers users who
shrink Windows themselves, without taking responsibility for resizing
another OS's filesystem.  Add "Alongside" only after the guided flow and
editor are stable, and treat it as a separate project with its own QEMU
tests.

### 4.7 Answer file v3

Keep v2 compatible.  Add a simpler top-level form for the guided modes:

```json
{
  "version": 3,
  "mode": "erase-disk",
  "disk": "/dev/nvme0n1",
  "filesystem": "ext4",
  "swap": "swapfile",
  "encrypt": false,
  "package_set": "desktop",
  "hostname": "tenko",
  "timezone": "Europe/Berlin",
  "locale": "en_US.UTF-8",
  "keymap": "us",
  "admin": {"username": "admin", "password": "change-me"},
  "confirm": {"phrase": "ERASE"}
}
```

The UI should be able to **export** this from the review page (to the ESP or
a USB stick) and **import** it for a repeatable install.  That closes the
loop between interactive and unattended installs and is a feature small
distributions rarely have.

### 4.8 Wizard state machine

Replace the nested function-call flow with an explicit state object:

```python
@dataclass
class WizardState:
    mode: str                 # erase-disk | free-space | custom
    disk_path: str | None
    filesystem: str
    swap_mode: str
    encrypt: bool
    timezone: str
    locale: str
    keymap: str
    hostname: str
    admin_user: str
    admin_password: str
    package_set: str
    layout: InstallSpec | None
```

A small controller with `next()`, `back()` and `validate()` is enough.  The
curses screens become render/input functions over the state.  This also
fixes the recursive `_interactive` call on a cancelled confirmation and
makes the flow testable without a terminal.

### 4.9 TUI toolkit extensions

`ui.py` needs a few widgets to support the mock-ups:

* `checkboxes` / `radio` / `select` fields in `form`, with left/right and
  space toggling.
* `table` with columns, a selected row and per-row action hints.
* `disk_map` bar with proportional segments and a legend.
* `step_header` (breadcrumb) and `status_line` (inline errors).
* `scrollable_text` for help and the full log.
* Color pairs when `curses.has_colors()`; 8-color fallback; no color
  requirement.
* Optional mouse (`curses.mousemask`); keyboard remains the primary input.
* Unicode box drawing only when the locale and terminal support it; the
  current ASCII-safe path must remain the default for `TERM=linux` and
  serial.

This is a contained change: the rest of the installer does not need to know
how a row is drawn.

## 5. Shell choice: TUI, GTK or web?

The current live image is console-only.  `tenko-live` pulls in
`tenko-base-runtime`, Python, ncurses, dnf, dracut and the filesystem
tools; there is no Xorg, no Wayland compositor and no browser.

| Option | What it takes | Pros | Cons |
| --- | --- | --- | --- |
| A. Modernized TUI (recommended) | Extend `ui.py`; no new packages | Small, fast, serial-friendly, matches the existing backend; can look good with color/layout/mouse | Not a "graphical installer"; some users equate TUI with old |
| B. GTK3 on Xorg | Add `gtk3`, `xorg-server`, `xorg` drivers, fonts, `lightdm`/kiosk setup to the live image; write a GTK front end | Native desktop look; GTK3 is in BLFS | Live image and ISO grow substantially; driver/GPU risk; a second UI to maintain; no serial fallback |
| C. Web UI kiosk (Anaconda/Agama style) | Local HTTP API + HTML/JS + a browser + a display server | Modern look; remote install possible | Largest dependency and attack surface; browser kiosk setup; still needs a display server |
| D. Remote web UI (no local browser) | HTTP server + HTML/JS; user opens it from another machine; console keeps the TUI | Modern UI without shipping a browser; good for servers/headless | Requires network; not useful for the common single-machine desktop install; security/authentication work |

Recommendation: **A now, D later if a graphical experience is wanted.**
The flow redesign is independent of the renderer, and a TUI that is fast and
clear is a better installer than a GUI that hides the same broken flow.

If the goal is explicitly "a graphical installer on the ISO", then B is the
straightforward path given the repo's X11-only desktop stack.  It should be
scheduled as its own milestone, reuse the same `WizardState`/planner, and be
tested in QEMU with the same scenarios as the TUI.  Do not make the TUI wait
for it.

## 6. Suggested roadmap

Milestone 0 and the core of Milestone 1 are implemented (see "Status" at the
top); the remaining milestones are still open.

### Milestone 0: quick wins (no new backend)

* Make Enter on a partition row open the edit action; add direct `d`/`n`/`f`
  keys.
* Show sizes in GiB with units; use `disk.human_size` everywhere.
* Show the free-space regions on the disk screen.
* Make "Use the entire disk" a one-action default that marks all existing
  partitions for deletion explicitly.
* Remove the swap partition from the default layout (see 4.2; can be staged
  after the UI change, but do not keep it as the default).
* Fix the root-disk wording: show a `*` on the disk that will receive `/`,
  and let the user pick it explicitly.
* Replace the recursive confirmation retry with a loop.
* Fix the "Back" paths so they return to the previous screen without
  re-running preflight.

Acceptance: a blank 20 GiB disk installs in four confirmations (welcome,
erase, account, review) with no partition editor and no typed sizes.

### Milestone 1: guided flow

* `WizardState` + controller.
* Screen 2 (where to install) with disk map and mode choices.
* Account page with timezone/keymap.
* Review page with ERASE/CREATE/KEEP groups.
* `plan_erase_disk` / `plan_free_space` in `layout.py`.
* Answer-file v3 guided form + export.
* `--simulate` scenarios for blank, existing ESP, free space, no free space.

Acceptance: the guided path covers a blank disk and a disk with an existing
ESP; the review page matches the generated plan exactly.

### Milestone 2: advanced editor

* Table view with direct row actions.
* Action sheet with mount point, filesystem, size, format, delete.
* Inline validation and retained input.
* Multi-disk "Add disk..." flow.
* Plain-mode guided prompts (serial parity).

Acceptance: an existing Windows disk with a 100 MiB ESP can be kept, an
existing data partition can be adopted at `/home`, and a new root can be
created in free space, all without typing a partition number or a MiB value.

### Milestone 3: storage features

* Swapfile default and fstab integration.
* LUKS2 (planner, install steps, crypttab, dracut, kernel cmdline).
* Btrfs subvolumes and mount options (if kept in scope).
* Existing-OS labels.
* Timezone/locale/keymap in the installed system.
* QEMU tests for encryption and btrfs.

Acceptance: encrypted install boots and unlocks; swapfile is active; btrfs
root mounts with the expected subvolumes; timezone and keymap survive
reboot.

### Milestone 4: optional graphical front end

* GTK3 front end over the same `WizardState`/planner, or a local web UI.
* Live-image dependency and ISO-size budget.
* Same QEMU scenario suite.
* Keep the TUI as the default/serial fallback.

## 7. Open questions

1. **Renderer:** is "modern" expected to mean a graphical installer, or is a
   substantially better TUI acceptable for this cycle?  The answer changes
   the schedule more than any other decision.
2. **Dual boot:** is "use existing free space" enough for the first release,
   or is "shrink Windows and install alongside" a must-have?  The latter
   needs ntfsresize, BitLocker detection and a separate safety story.
3. **Encryption:** passphrase-only LUKS2 first, or also TPM2 unlock with a
   recovery key?  TPM2 is a bigger design and support surface.
4. **Btrfs:** do we want subvolumes/snapshots now, or is ext4 the supported
   default with btrfs as a plain filesystem?
5. **ISO size:** is there a budget for Xorg/GTK3 (or a browser) in the live
   image, and does the live image need to keep working on serial/VGA only?
6. **XBOOTLDR:** issue #16 decides whether kernels stay on a 1 GiB ESP or
   move to an XBOOTLDR partition.  The guided layout, the review page and
   the "keep existing ESP" logic should follow that decision.

## 8. References

* Fedora Anaconda Web UI: <https://fedoraproject.org/wiki/Changes/Anaconda_Web_UI_Partitioning>
* Fedora Magazine, "Anaconda Web UI storage feedback": <https://fedoramagazine.org/anaconda-web-ui-storage-feedback-requested>
* Ubuntu 26.04 installation guide: <https://ubuntu.com/tutorials/install-ubuntu-desktop>
* openSUSE Agama storage documentation: <https://agama-project.github.io/docs/user/storage>
* Agama 18 storage UI redesign: <https://9to5linux.com/opensuse-releases-agama-18-installer-with-cleaner-and-more-intuitive-storage-ui>
* Calamares partitioning configuration: <https://calamares.io/docs/modules/partition/>
* archinstall disk configuration: <https://github.com/archlinux/archinstall>
* Debian installer partitioning: <https://www.debian.org/releases/stable/amd64/ch06s03.en.html>
