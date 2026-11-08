#!/bin/sh
# Find the Tenko ISO on a Ventoy data partition and give it to dmsquash-live.
#
# Queued by the 95tenko-ventoy udev rule when the VTOYEFI partition appears,
# so it never runs on a normal CD or dd-written USB boot.  Ventoy only maps
# the ISO inside the firmware; for the kernel it is just a *.iso file on the
# data partition.  Loop that file and run dmsquash-live-root directly; the
# initqueue is waiting for the live root.

command -v info > /dev/null || . /lib/dracut-lib.sh

PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH

TENKO_LABEL=TENKO
MNT=/run/initramfs/tenko-ventoy
ISO_LIST=/tmp/tenko-ventoy-isos

# A real CD or a dd-written stick already provides the label.
[ -e "/dev/disk/by-label/$TENKO_LABEL" ] && exit 0

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

# The data partition is usually ready before VTOYEFI (same disk, partition 1
# before partition 2), but retry briefly in case udev reports them out of
# order.  This wait only happens on a Ventoy boot.
i=0
while [ "$i" -lt 25 ]; do
    for dev in /dev/disk/by-uuid/*; do
        [ -e "$dev" ] || continue
        case "$(readlink -f "$dev")" in
            /dev/loop*) continue ;;
        esac
        try_device "$dev" && exit 0
    done
    i=$((i + 1))
    sleep 0.2
done

exit 1
