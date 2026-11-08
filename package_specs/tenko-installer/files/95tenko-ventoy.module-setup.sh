#!/bin/bash
# Expose a Tenko ISO stored on a Ventoy data partition to dmsquash-live.
#
# Ventoy's UEFI chain loader boots the ISO's own systemd-boot, which only
# reads the El Torito FAT image and never the ISO9660 filesystem.  The kernel
# therefore cannot see the ISO file and root=live:CDLABEL=TENKO waits
# forever.  This module finds the ISO on the Ventoy disk, loop-mounts it and
# hands it to dmsquash-live.  A real CD or a dd-written stick already has the
# TENKO label and never runs the scan.

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
    inst_hook initqueue 05 "$moddir/tenko-ventoy-iso.sh"
}
