#!/bin/sh
# Find the Tenko ISO on a Ventoy data partition and give it to dmsquash-live.
#
# dmsquash-live has already asked udev for /dev/disk/by-label/TENKO.  Ventoy
# only maps the ISO inside the firmware, so once the kernel runs the media is
# a *.iso file on the Ventoy data partition.  Loop that file and run
# dmsquash-live-root directly; the initqueue is waiting for the live root.
#
# A real CD or a dd-written USB stick already provides the label, so this
# exits immediately there.  Without a VTOYEFI partition (every non-Ventoy
# boot) it also does nothing.

command -v info > /dev/null || . /lib/dracut-lib.sh

PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH

TENKO_LABEL=TENKO
VTOY_LABEL=VTOYEFI
MNT=/run/initramfs/tenko-ventoy
ISO_LIST=/tmp/tenko-ventoy-isos

[ -e "/dev/disk/by-label/$TENKO_LABEL" ] && exit 0

# Only a Ventoy disk has a VTOYEFI partition.  Give udev a moment to publish
# it, then give up: a normal live boot must not be delayed by this scan.
i=0
while [ ! -e "/dev/disk/by-label/$VTOY_LABEL" ]; do
    i=$((i + 1))
    [ "$i" -gt 100 ] && exit 0
    sleep 0.1
done

mkdir -p "$MNT"

try_device() {
    dev="$1"
    mount -t auto -o ro "$dev" "$MNT" 2>/dev/null || return 1

    find "$MNT" -maxdepth 3 -type f -iname '*.iso' 2>/dev/null > "$ISO_LIST"
    while IFS= read -r iso; do
        loop=$(losetup --find --show --read-only "$iso" 2>/dev/null) || continue
        label=$(blkid -s LABEL -o value "$loop" 2>/dev/null)
        if [ "$label" = "$TENKO_LABEL" ]; then
            info "Found the Tenko live image at $iso on $dev ($loop)"
            # Publish the label as well, so later initramfs code can find
            # the media under its normal name.  Keep the backing filesystem
            # mounted while the loop device is in use.
            mkdir -p /dev/disk/by-label
            ln -sfn "$loop" "/dev/disk/by-label/$TENKO_LABEL"
            /sbin/dmsquash-live-root "$loop"
            return 0
        fi
        losetup -d "$loop" 2>/dev/null
    done < "$ISO_LIST"

    umount "$MNT" 2>/dev/null
    return 1
}

for dev in /dev/disk/by-uuid/*; do
    [ -e "$dev" ] || continue
    case "$(readlink -f "$dev")" in
        /dev/loop*) continue ;;
    esac
    try_device "$dev" && exit 0
done

exit 1
