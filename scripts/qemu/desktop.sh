#!/usr/bin/env bash
# Boot a graphical XFCE session in QEMU and capture a screenshot.
#
# Installs tenko-base + xfce-desktop from the single repo into
# build/rootfs-desktop, starts X on
# tty1 through a one-shot systemd unit, and uses the QEMU monitor to take a
# screendump of the VGA output.
#
# Usage:
#   tenko qemu desktop            # full run
#   SKIP_INSTALL=1 tenko qemu desktop   # reuse the rootfs/image
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
ROOTFS=${ROOTFS:-$PWD/build/rootfs-desktop}
REPO=${REPO:-$TENKO_REPO_URL}
REPOPATH=$(repo_url "$REPO")
IMG=${IMG:-$PWD/build/rootfs-desktop.img}
SERIAL=${SERIAL:-$PWD/build/qemu-graphical-serial.log}
MON=${MON:-$PWD/build/qemu-graphical-monitor.sock}
SHOT=${SHOT:-$PWD/build/xfce-screenshot.png}
WAIT=${WAIT:-90}
SKIP_INSTALL=${SKIP_INSTALL:-0}
USE_INITRD=${USE_INITRD:-1}
IMGSIZE=${IMGSIZE:-4G}
# Test-only packages installed from the repo (dependency-checked) and/or RPM
# files installed after the transaction with dependency checks bypassed.
EXTRA_PACKAGES=${EXTRA_PACKAGES:-}
EXTRA_RPMS=${EXTRA_RPMS:-}

if [ -d "$REPO" ]; then
    ls "$REPO"/xfce-desktop-*.rpm >/dev/null 2>&1 || {
        echo "repo has no xfce-desktop" >&2; exit 1; }
else
    case "$REPO" in
        http://*|https://*|ftp://*) ;;
        *) echo "missing repo: $REPO" >&2; exit 1 ;;
    esac
fi

if [ "$SKIP_INSTALL" != "1" ]; then
    echo "installing desktop rootfs (base + xfce-desktop)"
    # CA trust directories are read-only; remove them with fake-root
    # privileges so a rebuild can start from a clean tree.
    unshare -r rm -rf "$ROOTFS"
    mkdir -p "$ROOTFS/dev"
    # The fake-root build cannot mknod; regular files are enough for the
    # redirections and helpers the scriptlets use.
    for dev in null zero random urandom; do : > "$ROOTFS/dev/$dev"; done

    # Lay down the merged-/usr symlinks before DNF creates /lib as a real
    # directory in the installroot; otherwise tenko-basefs cannot unpack.
    unshare -r dnf -y --nogpgcheck \
        --installroot "$ROOTFS" --releasever="$TENKO_RELEASE" \
        --disablerepo='*' --repofrompath=desktop,$REPOPATH \
        --setopt=install_weak_deps=False --setopt=tsflags=noscripts \
        install tenko-basefs

    unshare -r dnf -y --nogpgcheck \
        --installroot "$ROOTFS" --releasever="$TENKO_RELEASE" \
        --disablerepo='*' --repofrompath=desktop,$REPOPATH \
        --setopt=install_weak_deps=False --setopt=tsflags=noscripts \
        install tenko-base xfce-desktop linux-kernel linux-modules \
        ${EXTRA_PACKAGES}

    if [ -x "$ROOTFS/usr/bin/systemd-sysusers" ]; then
        unshare -r chroot "$ROOTFS" /usr/bin/systemd-sysusers || true
    fi
    if [ -x "$ROOTFS/usr/bin/systemctl" ]; then
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ preset-all || true
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ enable dbus.socket || true
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ mask getty@tty1.service || true
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ mask lightdm.service || true
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ mask kmsconvt@tty1.service || true
        rm -f "$ROOTFS/etc/systemd/system/getty.target.wants/getty@tty1.service"
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ set-default graphical.target || true
    fi

    unshare -r chroot "$ROOTFS" /sbin/ldconfig || true
    if command -v depmod >/dev/null 2>&1; then
        depmod -b "$ROOTFS" "$KVER" || true
    elif [ -x "$ROOTFS/usr/sbin/depmod" ]; then
        unshare -r chroot "$ROOTFS" /usr/sbin/depmod -a "$KVER" || true
    fi
fi

if [ -n "$EXTRA_RPMS" ]; then
    echo "installing extra test RPMs (dependency checks bypassed)"
    # The binaries are test payloads; git/make-ca may not be packaged yet.
    # shellcheck disable=SC2086
    unshare -r rpm --root "$ROOTFS" -Uvh --replacepkgs --nodeps $EXTRA_RPMS
fi

# The kernel %post is skipped during rootfs assembly; make sure the image
# carries the initramfs it would have built.
if [ ! -f "$ROOTFS/boot/initramfs-$KVER.img" ] && [ -x "$ROOTFS/usr/bin/dracut" ]; then
    "$PWD/scripts/image/initramfs.sh" "$ROOTFS" "$KVER"
fi

# One-shot X session for the test: root, tty1, no login required.  The
# wrapper records the environment, the X lock state and the startx exit
# status so an intermittent failure is not silent on the serial console.
cat > "$ROOTFS/usr/local/bin/xfce-test-startx.sh" <<'EOF'
#!/bin/sh
log=/run/xfce-test-startx.log
exec >>"$log" 2>&1
echo "=== startx wrapper $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
echo "--- environment ---"
env | sort
mkdir -p /run/user/0 /tmp/.X11-unix
chmod 700 /run/user/0
chmod 1777 /tmp/.X11-unix
rm -f /tmp/.X0-lock /tmp/.X11-unix/X0
echo "--- startx ---"
/usr/bin/startx -- :0 vt1 -ac
rc=$?
echo "startx exit status: $rc"
exit "$rc"
EOF
chmod 0755 "$ROOTFS/usr/local/bin/xfce-test-startx.sh"
cat > "$ROOTFS/etc/systemd/system/xfce-test.service" <<'EOF'
[Unit]
Description=Start XFCE on tty1 (graphical boot test)
After=dbus.service

[Service]
Type=simple
User=root
Environment=HOME=/root
Environment=XDG_RUNTIME_DIR=/run/user/0
Environment=GTK_THEME=Default
TTYPath=/dev/tty1
StandardInput=tty
StandardOutput=journal+console
ExecStart=/usr/local/bin/xfce-test-startx.sh
Restart=no
TimeoutStartSec=30

[Install]
WantedBy=graphical.target
EOF
cat > "$ROOTFS/usr/local/bin/xfce-debug.sh" <<'EOF'
#!/bin/sh
export DISPLAY=:0 XAUTHORITY=/root/.Xauthority
mkdir -p /mnt
mount -t 9p -o trans=virtio,version=9p2000.L host0 /mnt 2>/dev/null || true
{
    echo "===VT==="; cat /sys/class/tty/tty0/active 2>&1
    echo "===PROCS==="; ps -ef
    echo "===PANELCFG==="; cat /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml 2>&1
    echo "===XWININFO==="; xwininfo -root -tree 2>&1
    echo "===COMPOSITING==="; xfconf-query -c xfwm4 -p /general/use_compositing 2>&1
    echo "===GLMODULES==="; ls -l /usr/lib64/xorg/modules/extensions/ /usr/lib64/dri/ 2>&1
    echo "===JOURNAL==="; journalctl -b -o short
    echo "===XORG==="; cat /var/log/Xorg.0.log 2>&1
    echo "===STARTX==="; cat /run/xfce-test-startx.log 2>&1
} > /mnt/debug.txt 2>&1
xwd -root -out /mnt/root.xwd 2>>/mnt/debug.txt
EOF
chmod 755 "$ROOTFS/usr/local/bin/xfce-debug.sh"

cat > "$ROOTFS/etc/systemd/system/xfce-debug.service" <<'EOF'
[Unit]
Description=Dump session state to the 9p share
After=xfce-test.service
Wants=xfce-test.service

[Service]
Type=oneshot
ExecStartPre=/bin/sleep 20
ExecStart=/usr/local/bin/xfce-debug.sh
TimeoutStartSec=60

[Install]
WantedBy=graphical.target
EOF

mkdir -p "$ROOTFS/etc/systemd/system/graphical.target.wants" "$PWD/build/qemu-share"
ln -sf ../xfce-test.service "$ROOTFS/etc/systemd/system/graphical.target.wants/xfce-test.service"
ln -sf ../xfce-debug.service "$ROOTFS/etc/systemd/system/graphical.target.wants/xfce-debug.service"

# Test-session defaults: GLX is available (Mesa/llvmpipe), so enable the
# xfwm4 compositor; use the built-in GTK "Default" theme.
mkdir -p "$ROOTFS/root/.config/xfce4/xfconf/xfce-perchannel-xml"
cat > "$ROOTFS/root/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfwm4" version="1.0">
  <property name="general" type="empty">
    <property name="use_compositing" type="bool" value="true"/>
  </property>
</channel>
EOF
cat > "$ROOTFS/root/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xsettings" version="1.0">
  <property name="Net" type="empty">
    <property name="ThemeName" type="string" value="Default"/>
    <property name="IconThemeName" type="string" value="hicolor"/>
  </property>
</channel>
EOF

# Temporary root password for interactive debugging (root/root).
hash=$(openssl passwd -6 root)
unshare -r sed -i "s|^root:[^:]*:|root:${hash}:|" "$ROOTFS/etc/shadow"

if [ ! -f "$IMG" ] || [ "${REBUILD_IMG:-1}" = "1" ]; then
    echo "building ext4 image"
    rm -f "$IMG"
    truncate -s "$IMGSIZE" "$IMG"
    unshare -r /usr/sbin/mke2fs -q -t ext4 -d "$ROOTFS" "$IMG"
fi

[ -f "$ROOTFS/boot/vmlinuz-$KVER" ] || { echo "missing kernel in $ROOTFS/boot" >&2; exit 1; }

if [ "${BUILD_ONLY:-0}" = "1" ]; then
    echo "image ready: $IMG"
    echo "boot it with: tenko qemu run"
    exit 0
fi

rm -f "$MON" "$SERIAL" "$SHOT"
initrd=()
if [ "$USE_INITRD" = 1 ] && [ -f "$ROOTFS/boot/initramfs-$KVER.img" ]; then
    initrd=(-initrd "$ROOTFS/boot/initramfs-$KVER.img")
fi
qemu-system-x86_64 \
    -enable-kvm -cpu host -m 3072 -smp 4 \
    -kernel "$ROOTFS/boot/vmlinuz-$KVER" \
    "${initrd[@]}" \
    -append "root=/dev/vda rw console=ttyS0 loglevel=6 systemd.show_status=1" \
    -drive file="$IMG",format=raw,if=virtio \
    -vga std \
    -display none -vnc 127.0.0.1:1 \
    -monitor "unix:$MON,server,nowait" \
    -serial "file:$SERIAL" \
    -virtfs "local,path=$PWD/build/qemu-share,mount_tag=host0,security_model=none" \
    -no-reboot &
qpid=$!
trap 'kill $qpid 2>/dev/null || true' EXIT

echo "qemu pid $qpid; waiting ${WAIT}s for the session"
sleep "$WAIT"

if [ ! -S "$MON" ]; then
    echo "monitor socket missing" >&2
    tail -40 "$SERIAL" >&2 || true
    exit 1
fi

# Prefer the in-guest X root-window capture: the QEMU std-VGA framebuffer
# dump comes out blank with the modesetting driver.
if [ -s "$PWD/build/qemu-share/root.xwd" ]; then
    convert "$PWD/build/qemu-share/root.xwd" "$SHOT"
    echo "screenshot: $SHOT (guest xwd)"
else
    printf 'screendump %s\n' "$PWD/build/xfce-screen.ppm" | socat - "UNIX-CONNECT:$MON" >/dev/null
    sleep 2
    if [ -s "$PWD/build/xfce-screen.ppm" ]; then
        convert "$PWD/build/xfce-screen.ppm" "$SHOT"
        echo "screenshot: $SHOT (qemu screendump)"
    else
        echo "no screenshot produced" >&2
    fi
fi

printf 'quit\n' | socat - "UNIX-CONNECT:$MON" >/dev/null || true
wait $qpid 2>/dev/null || true
trap - EXIT

echo "--- serial tail ---"
tail -40 "$SERIAL" || true
