#!/usr/bin/env bash
# Boot the prepared XFCE test image interactively.
#
# The image autostarts an XFCE session on tty1 as root (root password: root).
# Choose how to see it:
#
#   scripts/qemu_run_desktop.sh                 # GTK window if $DISPLAY is set, else VNC
#   DISPLAY_MODE=vnc scripts/qemu_run_desktop.sh
#   DISPLAY_MODE=gtk scripts/qemu_run_desktop.sh
#   VNC_ADDR=0.0.0.0:1 DISPLAY_MODE=vnc scripts/qemu_run_desktop.sh   # expose on the LAN
#
# VNC:   connect to 127.0.0.1:5901 (display :1)
# Serial: socat -,raw,echo=0 UNIX-CONNECT:build/xfce-serial.sock
#         (log in as root, password root)
# Stop:  Ctrl-C
set -euo pipefail
cd "$(dirname "$0")/.."

IMG=${IMG:-$PWD/build/xfce-test.img}
ROOTFS=${ROOTFS:-$PWD/build/rootfs-xfce-test}
KVER=${KVER:-7.2.6}
MEM=${MEM:-3072}
SMP=${SMP:-4}
SNAPSHOT=${SNAPSHOT:-1}
DISPLAY_MODE=${DISPLAY_MODE:-auto}
VNC_ADDR=${VNC_ADDR:-127.0.0.1:1}
SERIAL=${SERIAL:-$PWD/build/xfce-serial.sock}
MON=${MON:-$PWD/build/xfce-monitor.sock}
# Optional host->guest SSH forward, e.g. SSH_FWD=2222 -> ssh -p 2222 root@127.0.0.1
SSH_FWD=${SSH_FWD:-}

# Test-only extras: repo packages (default opencode-bin + herdr) and any
# RPM files found in build/extra-rpms.
EXTRA_PACKAGES=${EXTRA_PACKAGES-openssh opencode-bin herdr}
EXTRA_RPMS=${EXTRA_RPMS:-}
if [ -z "$EXTRA_RPMS" ] && [ -d "$PWD/build/extra-rpms" ]; then
    EXTRA_RPMS=$(find "$PWD/build/extra-rpms" -maxdepth 1 -name '*.rpm' -print | sort | tr '\n' ' ')
fi

# Rebuild if the image predates the requested extras.
if [ -n "$EXTRA_RPMS" ] && [ -f "$IMG" ]; then
    if [ ! -x "$ROOTFS/usr/bin/opencode" ] || [ ! -x "$ROOTFS/usr/bin/herdr" ]; then
        echo "image is missing requested test binaries; rebuilding with extras" >&2
        rm -f "$IMG"
    fi
fi

if [ ! -f "$IMG" ]; then
    echo "no image at $IMG; building it from build/repo-all (this takes a minute)"
    ROOTFS="$ROOTFS" IMG="$IMG" SKIP_INSTALL=0 BUILD_ONLY=1 \
        IMGSIZE="${IMGSIZE:-5G}" EXTRA_PACKAGES="$EXTRA_PACKAGES" \
        EXTRA_RPMS="$EXTRA_RPMS" \
        "$PWD/scripts/qemu_boot_graphical.sh"
fi

case "$DISPLAY_MODE" in
    auto)
        if [ -n "${DISPLAY:-}" ]; then DISPLAY_MODE=gtk; else DISPLAY_MODE=vnc; fi
        ;;
esac

kvm=()
if [ -w /dev/kvm ]; then
    kvm=(-enable-kvm -cpu host)
else
    echo "warning: /dev/kvm not writable; running under TCG (slow)" >&2
    kvm=(-cpu max)
fi

snap=()
[ "$SNAPSHOT" = "1" ] && snap=(-snapshot)

# Graphics device.  virtio-vga-gl is the virtio-gpu device with the 3D
# (virgl) capability and needs a display backend with OpenGL (gtk/sdl with
# gl=on); vnc/none cannot supply one, so those modes fall back to the 2D
# virtio-vga.  Note the guest side also needs Mesa's virgl gallium driver for
# accelerated GL - this distro builds llvmpipe only, so the guest still
# software-renders; the device choice only changes the display path.
# Override with VGA=std|virtio-vga|qxl|... .
VGA=${VGA:-virtio-vga-gl}

gl=0
display=()
case "$DISPLAY_MODE" in
    gtk|sdl) display=(-display "$DISPLAY_MODE"); gl=1 ;;
    vnc)     display=(-display none -vnc "$VNC_ADDR") ;;
    none)    display=(-display none) ;;
    *)       echo "unknown DISPLAY_MODE: $DISPLAY_MODE" >&2; exit 1 ;;
esac

vga=()
case "$VGA" in
    virtio-vga-gl)
        if [ "$gl" = 1 ]; then
            display=(-display "$DISPLAY_MODE,gl=on")
            vga=(-device virtio-vga-gl)
        else
            echo "note: virtio-vga-gl needs an OpenGL display backend" \
                 "($DISPLAY_MODE has none); using virtio-vga" >&2
            vga=(-device virtio-vga)
        fi
        ;;
    virtio-vga|virtio-gpu-pci|qxl)
        vga=(-device "$VGA") ;;
    std|cirrus|vmware|xenfb|none)
        vga=(-vga "$VGA") ;;
    *)
        echo "unknown VGA: $VGA" >&2; exit 1 ;;
esac

rm -f "$SERIAL" "$MON"

nic=()
if [ -n "$SSH_FWD" ]; then
    nic=(-nic "user,model=virtio-net-pci,hostfwd=tcp:127.0.0.1:${SSH_FWD}-:22")
fi

initrd=()
if [ "${USE_INITRD:-1}" = 1 ] && [ -f "$ROOTFS/boot/initramfs-$KVER.img" ]; then
    initrd=(-initrd "$ROOTFS/boot/initramfs-$KVER.img")
fi

cat <<EOF
Browneye XFCE test boot
  image:   $IMG (snapshot=$SNAPSHOT)
  login:   root / root (tty1 is occupied by the X session)
  display: $DISPLAY_MODE${DISPLAY_MODE:+ }
  video:   $VGA$([ "$gl" = 1 ] && echo " (gl=on)")
EOF
if [ "$DISPLAY_MODE" = "vnc" ]; then
    port=$((5900 + ${VNC_ADDR##*:}))
    echo "  VNC:     ${VNC_ADDR%:*}:$port  (e.g. vncviewer 127.0.0.1:$port)"
fi
cat <<EOF
  serial:  socat -,raw,echo=0 UNIX-CONNECT:$SERIAL
  monitor: socat - UNIX-CONNECT:$MON   (screendump/sendkey)
  stop:    Ctrl-C
EOF
if [ -n "$SSH_FWD" ]; then
    echo "  SSH:     ssh -p $SSH_FWD root@127.0.0.1"
fi
echo

exec qemu-system-x86_64 \
    "${kvm[@]}" "${snap[@]}" \
    -m "$MEM" -smp "$SMP" \
    -kernel "$ROOTFS/boot/vmlinuz-$KVER" \
    "${initrd[@]}" \
    "${nic[@]}" \
    -append "root=/dev/vda rw console=ttyS0 loglevel=6 systemd.show_status=1" \
    -drive "file=$IMG,format=raw,if=virtio" \
    "${vga[@]}" \
    "${display[@]}" \
    -monitor "unix:$MON,server,nowait" \
    -serial "unix:$SERIAL,server,nowait" \
    -no-reboot
