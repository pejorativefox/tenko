#!/bin/bash
# Expose a Tenko ISO stored on a Ventoy data partition to dmsquash-live.
#
# Ventoy's UEFI chain loader boots the ISO's own systemd-boot from the
# El Torito image, which cannot see the ISO9660 filesystem.  The kernel
# therefore never finds the ISO file and root=live:CDLABEL=TENKO waits
# forever.  This module finds the ISO on the Ventoy data partition, loop-
# mounts it and hands it to dmsquash-live.
#
# The udev rule makes this Ventoy-only: a normal CD or dd-written stick has
# no VTOYEFI partition, so nothing is queued and the boot is not delayed.

check() {
    return 0
}

depends() {
    echo "dmsquash-live"
}

installkernel() {
    hostonly='' instmods exfat vfat ntfs3 nls_cp437 nls_iso8859-1 nls_utf8 loop
}

install() {
    inst_multiple mount umount blkid losetup find readlink sleep
    inst_simple "$moddir/tenko-ventoy-iso.sh" /sbin/tenko-ventoy-iso
    inst_rules "$moddir/tenko-ventoy.rules"
}
