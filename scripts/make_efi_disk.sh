#!/usr/bin/env bash
# Build a GPT/UEFI disk image that boots Browneye with GRUB (no QEMU -kernel).
#
# Usage: scripts/make_efi_disk.sh [ROOTFS] [IMG] [KVER]
set -euo pipefail
cd "$(dirname "$0")/.."

ROOTFS=${1:-build/rootfs-xfce-test}
IMG=${2:-build/browneye-efi.img}
KVER=${3:-7.3.1}
ESP_MB=${ESP_MB:-64}
WORK=${WORK:-build/efi-work}

[ -f "$ROOTFS/boot/vmlinuz-$KVER" ] || { echo "missing $ROOTFS/boot/vmlinuz-$KVER" >&2; exit 1; }
mkdir -p "$WORK"

# GRUB configuration (embedded in the standalone EFI binary).
INITRD_LINE=""
if [ -f "$ROOTFS/boot/initramfs-$KVER.img" ]; then
    INITRD_LINE="    initrd /boot/initramfs-$KVER.img"
fi
cat > "$WORK/grub.cfg" <<EOF
set timeout=3
set default=0
menuentry 'Browneye Linux 13.1 (kernel $KVER)' {
    set root=(hd0,gpt2)
    linux /boot/vmlinuz-$KVER root=/dev/vda2 rw rootwait console=ttyS0 loglevel=7
$INITRD_LINE
}
EOF

# Standalone EFI application with the ext2/linux/gpt modules built in.
cp "$WORK/grub.cfg" build/blfs-parity-20261031/grub.cfg
podman exec browneye-blfs grub-mkstandalone -O x86_64-efi \
    -o /out/bootx64.efi \
    --modules="part_gpt part_msdos fat ext2 normal linux search search_fs_uuid" \
    "boot/grub/grub.cfg=/out/grub.cfg" >/dev/null
cp build/blfs-parity-20261031/bootx64.efi "$WORK/BOOTX64.EFI"
rm -f build/blfs-parity-20261031/grub.cfg build/blfs-parity-20261031/bootx64.efi

# EFI system partition (FAT32).
rm -f "$WORK/esp.img"
truncate -s "${ESP_MB}M" "$WORK/esp.img"
mkfs.vfat -F32 -n BOOT "$WORK/esp.img" >/dev/null
mmd -i "$WORK/esp.img" ::/EFI ::/EFI/BOOT
mcopy -i "$WORK/esp.img" "$WORK/BOOTX64.EFI" ::/EFI/BOOT/BOOTX64.EFI

# Root filesystem (populated from the installed rootfs).
ROOT_MB=$(du -sm "$ROOTFS" | awk '{print $1}')
ROOT_MB=$((ROOT_MB * 12 / 10 + 128))
rm -f "$WORK/root.img"
truncate -s "${ROOT_MB}M" "$WORK/root.img"
unshare -r mke2fs -q -t ext4 -m 0 -L browneye -d "$ROOTFS" "$WORK/root.img"

# Size the root partition from the image actually produced (mke2fs may round
# the filesystem up), plus one MiB of slack.
PART_MB=$(( ($(stat -c %s "$WORK/root.img") + 1048575) / 1048576 + 1 ))
PART_SECTORS=$((PART_MB * 2048))

# GPT: p1 = 64 MiB ESP at 1 MiB, p2 = root at 65 MiB.
ESP_SECTORS=$((ESP_MB * 2048))
ROOT_START=$((2048 + ESP_SECTORS))
rm -f "$IMG"
truncate -s "$(( (ROOT_START + PART_SECTORS + 2048) * 512 ))" "$IMG"
sfdisk --quiet "$IMG" <<EOF
label: gpt
start=2048, size=$ESP_SECTORS, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, name=EFI
start=$ROOT_START, size=$PART_SECTORS, type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name=browneye
EOF
dd if="$WORK/esp.img" of="$IMG" bs=1M seek=1 conv=notrunc status=none
dd if="$WORK/root.img" of="$IMG" bs=1M seek=$((ROOT_START / 2048)) conv=notrunc status=none

echo "wrote $IMG ($(du -h "$IMG" | cut -f1)); root=/dev/vda2, kernel $KVER"
