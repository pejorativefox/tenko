#!/usr/bin/env bash
# Boot the real first-boot flow and capture the LightDM greeter (C3/E1).
#
# Installs browneye-base + xfce-desktop (which now pulls lightdm) from the
# repo with scriptlets ENABLED, leaves the root account locked, and boots to
# graphical.target.  browneye-firstboot prompts on tty1; this script types a
# throwaway password through the QEMU monitor, then waits for the greeter and
# captures it (guest xwd over 9p, with a QEMU screendump fallback).
#
# Usage:
#   scripts/qemu_boot_login.sh                 # full run
#   SKIP_INSTALL=1 scripts/qemu_boot_login.sh  # reuse rootfs/image
#   BUILD_ONLY=1 scripts/qemu_boot_login.sh    # build rootfs+image, do not boot
#   EXTRA_PACKAGES="openssh" scripts/qemu_boot_login.sh
#
# The image is a test artifact: anyone who knows TEST_PASSWORD can log in.
set -euo pipefail
cd "$(dirname "$0")/.."

KVER=${KVER:-7.3.1}
ROOTFS=${ROOTFS:-$PWD/build/rootfs-login-test}
IMG=${IMG:-$PWD/build/login-test.img}
REPO=${REPO:-$PWD/build/repo-all}
SERIAL=${SERIAL:-$PWD/build/login-serial.log}
MON=${MON:-$PWD/build/login-monitor.sock}
SHOT=${SHOT:-$PWD/build/login-screenshot.png}
PROMPT_SHOT=${PROMPT_SHOT:-$PWD/build/login-firstboot.png}
SHARE=${SHARE:-$PWD/build/qemu-share}
IMGSIZE=${IMGSIZE:-6G}
SKIP_INSTALL=${SKIP_INSTALL:-0}
BUILD_ONLY=${BUILD_ONLY:-0}
EXTRA_PACKAGES=${EXTRA_PACKAGES:-}
EXTRA_RPMS=${EXTRA_RPMS:-}
TEST_USER=${TEST_USER:-}
WAIT_BOOT=${WAIT_BOOT:-40}
WAIT_GREETER=${WAIT_GREETER:-45}
TEST_PASSWORD=${TEST_PASSWORD:-browneye1}

[ -d "$REPO" ] || { echo "missing repo: $REPO" >&2; exit 1; }

if [ "$SKIP_INSTALL" != "1" ]; then
    echo "installing unified rootfs with scriptlets enabled"
    unshare -r rm -rf "$ROOTFS"
    mkdir -p "$ROOTFS/dev"
    # The fake-root build cannot mknod; regular files are enough for the
    # redirections and helpers the scriptlets use.
    for dev in null zero random urandom; do : > "$ROOTFS/dev/$dev"; done

    # Lay down the base filesystem first: every scriptlet runs through
    # /bin/sh, which only exists once browneye-basefs has created the merged
    # /usr symlinks.  This is what an installer does before anything else.
    unshare -r dnf -y --nogpgcheck \
        --installroot "$ROOTFS" --releasever=13.1 \
        --disablerepo='*' --repofrompath=browneye,file://$REPO \
        --setopt=install_weak_deps=False \
        install browneye-basefs

    unshare -r dnf -y --nogpgcheck \
        --installroot "$ROOTFS" --releasever=13.1 \
        --disablerepo='*' --repofrompath=browneye,file://$REPO \
        --setopt=install_weak_deps=False \
        install browneye-base xfce-desktop linux-kernel linux-modules \
        ${EXTRA_PACKAGES} \
        || echo "warning: dnf reported a scriptlet failure; checking packages" >&2

    if [ -n "$EXTRA_RPMS" ]; then
        echo "installing extra test RPMs (dependency checks bypassed)"
        # shellcheck disable=SC2086
        unshare -r rpm --root "$ROOTFS" -Uvh --replacepkgs --nodeps $EXTRA_RPMS
    fi

    for pkg in browneye-base xfce-desktop lightdm lightdm-gtk-greeter \
               linux-kernel linux-modules browneye-firstboot; do
        rpm -q --root "$ROOTFS" "$pkg" >/dev/null || {
            echo "missing package after install: $pkg" >&2; exit 1; }
    done

    # Presets are only applied when something asks systemd to apply them.
    if [ -x "$ROOTFS/usr/bin/systemctl" ]; then
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ preset-all || true
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ set-default graphical.target || true
    fi

    # The build runs as fake root, so lightdm's %post cannot chown its state
    # directories.  Make them writable for the test image.
    for d in var/lib/lightdm var/lib/lightdm-data var/cache/lightdm var/log/lightdm; do
        [ -d "$ROOTFS/$d" ] && chmod -R a+rwX "$ROOTFS/$d"
    done

    if [ -n "$TEST_USER" ]; then
        # A normal (UID >= 1000) account gives AccountsService something to
        # show in the greeter's user list.
        unshare -r chroot "$ROOTFS" /usr/sbin/useradd -m -c "Test User" "$TEST_USER" || true
    fi

    # Root must stay locked so browneye-firstboot prompts on first boot.
    if unshare -r chroot "$ROOTFS" passwd -S root 2>/dev/null | grep -q '^root P'; then
        echo "error: root already has a password; first boot would be skipped" >&2
        exit 1
    fi

    # Guest-side capture of the greeter: xwd against LightDM's X display.
    cat > "$ROOTFS/usr/local/bin/greeter-capture.sh" <<'EOF'
#!/bin/sh
mkdir -p /mnt
mount -t 9p -o trans=virtio,version=9p2000.L host0 /mnt 2>/dev/null || true
i=0
while [ "$i" -lt 45 ] && [ ! -S /tmp/.X11-unix/X0 ]; do
    sleep 2
    i=$((i + 1))
done
{
    echo "===X-SOCKETS==="; ls -l /tmp/.X11-unix 2>&1
    echo "===LIGHTDM-STATE==="; ls -l /run/lightdm /run/lightdm/root /var/lib/lightdm 2>&1
} > /mnt/greeter-capture.log 2>&1
for auth in /var/lib/lightdm/.Xauthority /run/lightdm/root/:0 /root/.Xauthority; do
    [ -e "$auth" ] || continue
    echo "trying XAUTHORITY=$auth" >> /mnt/greeter-capture.log
    if XAUTHORITY="$auth" DISPLAY=:0 xwd -root -silent -out /mnt/greeter.xwd \
            >> /mnt/greeter-capture.log 2>&1; then
        echo "captured with $auth" >> /mnt/greeter-capture.log
        break
    fi
done
{
    echo "===XORG-LOG==="; tail -100 /var/log/Xorg.0.log 2>&1
    echo "===LIGHTDM-LOG==="; tail -60 /var/log/lightdm/lightdm.log 2>&1
} >> /mnt/greeter-capture.log 2>&1
EOF
    chmod 755 "$ROOTFS/usr/local/bin/greeter-capture.sh"
    cat > "$ROOTFS/etc/systemd/system/greeter-capture.service" <<'EOF'
[Unit]
Description=Capture the LightDM greeter to the 9p share
After=lightdm.service
Wants=lightdm.service

[Service]
Type=oneshot
ExecStartPre=/bin/sleep 15
ExecStart=/usr/local/bin/greeter-capture.sh
TimeoutStartSec=180

[Install]
WantedBy=graphical.target
EOF
    mkdir -p "$ROOTFS/etc/systemd/system/graphical.target.wants"
    ln -sf ../greeter-capture.service \
        "$ROOTFS/etc/systemd/system/graphical.target.wants/greeter-capture.service"

    if [ ! -f "$ROOTFS/boot/initramfs-$KVER.img" ]; then
        "$PWD/scripts/make_initramfs.sh" "$ROOTFS" "$KVER"
    fi

    echo "building ext4 image"
    rm -f "$IMG"
    truncate -s "$IMGSIZE" "$IMG"
    unshare -r mke2fs -q -t ext4 -d "$ROOTFS" "$IMG"
fi

[ -f "$ROOTFS/boot/vmlinuz-$KVER" ] || { echo "missing kernel" >&2; exit 1; }

if [ "$BUILD_ONLY" = "1" ]; then
    echo "image ready: $IMG"
    exit 0
fi

rm -f "$MON" "$SERIAL" "$SHOT" "$PROMPT_SHOT"
mkdir -p "$SHARE"
rm -f "$SHARE/greeter.xwd" "$SHARE/greeter-capture.log"

initrd=()
[ -f "$ROOTFS/boot/initramfs-$KVER.img" ] && \
    initrd=(-initrd "$ROOTFS/boot/initramfs-$KVER.img")

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
    -virtfs "local,path=$SHARE,mount_tag=host0,security_model=none" \
    -no-reboot &
qpid=$!
trap 'kill $qpid 2>/dev/null || true' EXIT

mon() { printf '%s\n' "$*" | socat - "UNIX-CONNECT:$MON" >/dev/null 2>&1 || true; }
shot() {
    local out=$1 ppm="$SHARE/qemu-$2.ppm"
    mon "screendump $ppm" || true
    sleep 2
    if [ -s "$ppm" ]; then
        convert "$ppm" "$out" 2>/dev/null || true
        [ -s "$out" ] && { echo "screenshot: $out (qemu screendump)"; return 0; }
    fi
    return 1
}
type_text() {
    local s=$1
    for ((i = 0; i < ${#s}; i++)); do
        local c=${s:i:1}
        case "$c" in
            [a-z0-9]) mon "sendkey $c" ;;
            -) mon "sendkey minus" ;;
            .) mon "sendkey dot" ;;
            ' ') mon "sendkey spc" ;;
            *) echo "unsupported character: $c" >&2 ;;
        esac
        sleep 0.15
    done
    mon "sendkey ret"
}

echo "waiting ${WAIT_BOOT}s for the first-boot prompt"
sleep "$WAIT_BOOT"
shot "$PROMPT_SHOT" firstboot || echo "no first-boot screendump" >&2

echo "typing the first-boot root password on tty1"
type_text "$TEST_PASSWORD"
sleep 1
type_text "$TEST_PASSWORD"

echo "waiting ${WAIT_GREETER}s for LightDM"
sleep "$WAIT_GREETER"

if [ -s "$SHARE/greeter.xwd" ]; then
    convert "$SHARE/greeter.xwd" "$SHOT"
    echo "screenshot: $SHOT (guest xwd)"
else
    shot "$SHOT" greeter || echo "no greeter screendump" >&2
fi

echo "--- serial tail ---"
tail -40 "$SERIAL" || true
echo "--- capture log ---"
cat "$SHARE/greeter-capture.log" 2>/dev/null | head -30 || true

printf 'quit\n' | socat - "UNIX-CONNECT:$MON" >/dev/null 2>&1 || true
wait $qpid 2>/dev/null || true
trap - EXIT
