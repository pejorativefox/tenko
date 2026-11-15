#!/usr/bin/env bash
# Install onto disks that already have an ESP, under UEFI, and check that the
# installer adopts a usable one and refuses one that is too small.
#
# Usage:
#   tenko qemu esp-reuse              # both cases
#   tenko qemu esp-reuse refuse       # only the refusal case (a few minutes)
#   ISO=build/other.iso tenko qemu esp-reuse adopt
#
# Each case builds a 20 GiB GPT disk with a pre-existing 512 MiB FAT32 ESP
# (4 KiB clusters, like a real one) holding a marker file and filler data,
# boots the ISO's kernel with tenko.auto=1, and passes a version 3
# "free-space" answer file (base package set) through QEMU fw_cfg.
#
#   adopt   ESP ~200 MiB used (~310 MiB free, above ESP_MIN_FREE_MIB = 256).
#           Pass: the install reports OK, the ESP keeps its marker and filler
#           and gains systemd-boot, EFI/BOOT/BOOTX64.EFI and the kernel; with
#           an empty NVRAM the disk boots through the fallback loader to the
#           systemd-boot menu and multi-user.target, read back from the installed
#           journal.
#   refuse  ESP ~300 MiB used (~210 MiB free) plus a 1 GiB data partition.
#           Pass: the installer stops at the mount step with the "delete the
#           partition and let the installer create a larger ESP" remedy, the
#           data partition is byte-identical and the ESP files are intact.
#
# The installer installs from the network repository, so the guest needs
# internet access (QEMU user networking).  Work files and serial logs are in
# build/esp-reuse/.  Exit status: 0 every selected case passed.
#
# Environment: ISO (build/tenko-installer.iso), OUT (build/esp-reuse),
# MEM (6144), INSTALL_WAIT (2700 s), BOOT_WAIT (240 s), OVMF_CODE,
# OVMF_VARS_SRC.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"

ISO=$(abspath "${ISO:-build/tenko-installer.iso}")
OUT=$(abspath "${OUT:-build/esp-reuse}")
MEM=${MEM:-6144}
INSTALL_WAIT=${INSTALL_WAIT:-2700}
BOOT_WAIT=${BOOT_WAIT:-240}
OVMF_CODE=${OVMF_CODE:-/usr/share/edk2/ovmf/OVMF_CODE.fd}
OVMF_VARS_SRC=${OVMF_VARS_SRC:-/usr/share/edk2/ovmf/OVMF_VARS.fd}

ESP_START=2048            # sectors
ESP_SECTORS=1048576       # 512 MiB
DATA_START=$((ESP_START + ESP_SECTORS))
DATA_SECTORS=2097152      # 1 GiB
ESP_OFF=$((ESP_START * 512))

for tool in qemu-system-x86_64 sfdisk mkfs.fat mcopy mdir mtype bsdtar debugfs journalctl; do
    command -v "$tool" >/dev/null || die "missing $tool"
done
[ -f "$ISO" ] || die "missing ISO: $ISO (download it or set ISO)"
[ -f "$OVMF_CODE" ] && [ -f "$OVMF_VARS_SRC" ] || die "missing OVMF firmware: install edk2-ovmf"

mkdir -p "$OUT"
cd "$OUT"

# The ISO's kernel and initramfs, booted directly so tenko.auto=1 can be
# added to the boot entry's options.
extract_kernel() {
    [ -f vmlinuz ] && [ -f initrd.img ] && [ vmlinuz -nt "$ISO" ] && return
    bsdtar -xf "$ISO" boot/efiboot.img
    mcopy -o -i boot/efiboot.img ::/vmlinuz ::/initrd.img .
    mtype -i boot/efiboot.img ::/loader/entries/tenko.conf |
        sed -n 's/^options //p' | tr -d '\r' > options.txt
    rm -rf boot
}

# make_disk IMG USED_MIB [data]
make_disk() {
    local img=$1 used=$2 data=${3:-}
    rm -f "$img"
    truncate -s 20G "$img"
    {
        echo "label: gpt"
        echo "start=$ESP_START, size=$ESP_SECTORS, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, name=\"EFI System\""
        if [ -n "$data" ]; then
            echo "start=$DATA_START, size=$DATA_SECTORS, type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name=\"data\""
        fi
    } | sfdisk -q "$img"
    # -s 8: 4 KiB clusters.  Left to itself mkfs.fat sizes clusters from the
    # whole image, and a FAT32 with too few clusters is FAT16 to UEFI.
    mkfs.fat -F 32 -s 8 -n OLDESP --offset "$ESP_START" "$img" $((ESP_SECTORS / 2)) >/dev/null 2>&1
    printf 'pre-existing ESP\n' > marker.txt
    mcopy -i "$img@@$ESP_OFF" marker.txt ::/OLD-MARKER.TXT
    mmd -i "$img@@$ESP_OFF" ::/EFI ::/EFI/vendor
    head -c $((used * 1024 * 1024)) /dev/urandom > filler.bin
    mcopy -i "$img@@$ESP_OFF" filler.bin ::/EFI/vendor/filler.bin
    sha256sum filler.bin | cut -d' ' -f1 > "${img%.img}-filler.sha256"
    rm -f marker.txt filler.bin
    if [ -n "$data" ]; then
        dd if=/dev/urandom of="$img" bs=1M seek=$((DATA_START / 2048)) \
           count=$((DATA_SECTORS / 2048)) conv=notrunc status=none
    fi
}

# region_sha IMG START_SECTOR SECTORS
region_sha() {
    dd if="$1" bs=1M skip=$(($2 / 2048)) count=$(($3 / 2048)) status=none |
        sha256sum | cut -d' ' -f1
}

esp_free_mib() {
    mdir -i "$1@@$ESP_OFF" :: | awk '/bytes free/ { gsub(/ /, "", $0); sub(/bytesfree/, "", $0); print int($0 / 1048576) }'
}

esp_files_intact() {
    local img=$1
    [ "$(mtype -i "$img@@$ESP_OFF" ::/OLD-MARKER.TXT)" = "pre-existing ESP" ] || return 1
    [ "$(mtype -i "$img@@$ESP_OFF" ::/EFI/vendor/filler.bin | sha256sum | cut -d' ' -f1)" = \
      "$(cat "${img%.img}-filler.sha256")" ]
}

# install NAME: unattended install onto NAME.img; prints the result marker.
install() {
    local name=$1
    cat > "answer-$name.json" <<'EOF'
{
  "version": 3,
  "mode": "free-space",
  "disk": "/dev/vda",
  "filesystem": "ext4",
  "swap": "none",
  "package_set": "base",
  "hostname": "tenko-esp",
  "admin": {"username": "admin", "password": "test-only"},
  "confirm": {"phrase": "ERASE"}
}
EOF
    chmod 600 "answer-$name.json"
    cp "$OVMF_VARS_SRC" "vars-$name.fd"
    rm -f "install-$name.log"
    # The target disk comes first so it is /dev/vda; the ISO is attached as
    # a read-only virtio disk (it keeps the TENKO label the live root uses).
    qemu-system-x86_64 -enable-kvm -cpu host -m "$MEM" -smp 4 \
        -drive if=pflash,format=raw,readonly=on,file="$OVMF_CODE" \
        -drive if=pflash,format=raw,file="vars-$name.fd" \
        -kernel vmlinuz -initrd initrd.img \
        -append "$(sed 's/console=tty0 //' options.txt) tenko.auto=1 tenko.console=serial" \
        -drive file="$name.img",format=raw,if=virtio \
        -drive file="$ISO",format=raw,if=virtio,readonly=on \
        -fw_cfg name=opt/tenko/answer.json,file="answer-$name.json" \
        -nic user,model=virtio-net-pci \
        -display none -serial file:"install-$name.log" -no-reboot &
    local pid=$! waited=0
    while kill -0 "$pid" 2>/dev/null; do
        grep -a -q -E '^TENKO-INSTALL: (OK|FAIL)' "install-$name.log" 2>/dev/null && break
        [ "$waited" -ge "$INSTALL_WAIT" ] && break
        sleep 5; waited=$((waited + 5))
    done
    # Give the installer a moment to finish writing logs, then stop the VM.
    sleep 5
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
    # Serial lines end in CRLF; drop the CR so the marker compares exactly.
    grep -a -E '^TENKO-INSTALL: (OK|FAIL)' "install-$name.log" | tail -1 | tr -d '\r' || true
}

# boot_installed IMG: boot with an empty NVRAM; succeeds when the installed
# journal shows multi-user.target reached in that boot.
boot_installed() {
    local img=$1
    cp "$OVMF_VARS_SRC" vars-boot.fd
    rm -f boot.log
    qemu-system-x86_64 -enable-kvm -cpu host -m 2048 -smp 2 \
        -drive if=pflash,format=raw,readonly=on,file="$OVMF_CODE" \
        -drive if=pflash,format=raw,file=vars-boot.fd \
        -drive file="$img",format=raw,if=virtio -nic none \
        -display none -serial file:boot.log -no-reboot &
    local pid=$!
    sleep "$BOOT_WAIT"
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
    grep -a -q 'Tenko Linux' boot.log || { echo "  no systemd-boot menu on serial"; return 1; }
    # Read the journal of the installed root (partition 2) offline.
    local start
    start=$(sfdisk -d "$img" | awk -F'[=,]' '/name="Tenko Linux"/ { gsub(/ /, "", $2); print $2 }')
    dd if="$img" of=root.part bs=512 skip="$start" conv=sparse status=none
    rm -rf journal
    debugfs -R "rdump /var/log/journal $OUT" root.part >/dev/null 2>&1 || true
    rm -f root.part
    journalctl -D journal -q --no-pager -o cat 2>/dev/null |
        grep -E 'Reached target .*[Mm]ulti-[Uu]ser' > boot-journal.txt || true
    [ -s boot-journal.txt ] || { echo "  installed journal never reached multi-user.target"; return 1; }
    sed 's/^/  journal: /' boot-journal.txt | sort -u
}

case_adopt() {
    echo "== adopt: 512 MiB ESP, ~200 MiB used"
    make_disk adopt.img 200
    sfdisk -d adopt.img | grep -F 'adopt.img1' > adopt-esp-entry.txt
    echo "  ESP free before install: $(esp_free_mib adopt.img) MiB"
    local result
    result=$(install adopt)
    echo "  $result"
    [ "$result" = "TENKO-INSTALL: OK" ] || return 1
    sfdisk -d adopt.img | grep -F -x -f adopt-esp-entry.txt >/dev/null || { echo "  ESP entry changed"; return 1; }
    esp_files_intact adopt.img || { echo "  ESP marker or filler changed"; return 1; }
    for f in ::/EFI/BOOT/BOOTX64.EFI ::/EFI/systemd/systemd-bootx64.efi ::/loader/loader.conf; do
        mdir -i "adopt.img@@$ESP_OFF" "$f" >/dev/null 2>&1 || { echo "  missing $f on the ESP"; return 1; }
    done
    # No grep -q on a pipe: under pipefail its early exit fails mdir.
    case "$(mdir -i "adopt.img@@$ESP_OFF" -b ::/)" in
        *"::/vmlinuz-"*) ;;
        *) echo "  no kernel on the ESP"; return 1 ;;
    esac
    echo "  ESP adopted without formatting; systemd-boot, fallback loader and kernel installed"
    boot_installed adopt.img
}

case_refuse() {
    echo "== refuse: 512 MiB ESP, ~300 MiB used, 1 GiB data partition"
    make_disk refuse.img 300 data
    echo "  ESP free before install: $(esp_free_mib refuse.img) MiB"
    local data_before result
    data_before=$(region_sha refuse.img "$DATA_START" "$DATA_SECTORS")
    result=$(install refuse)
    echo "  $result"
    case "$result" in
        "TENKO-INSTALL: FAIL mount: the ESP has only "*" MiB free"*) ;;
        *) return 1 ;;
    esac
    grep -a -q 'remedy=delete the partition and let the installer create a larger ESP' install-refuse.log ||
        { echo "  remedy missing from the log"; return 1; }
    [ "$(region_sha refuse.img "$DATA_START" "$DATA_SECTORS")" = "$data_before" ] ||
        { echo "  data partition changed"; return 1; }
    esp_files_intact refuse.img || { echo "  ESP marker or filler changed"; return 1; }
    echo "  refused at the mount step; data partition byte-identical, ESP files intact"
}

extract_kernel
cases=${*:-adopt refuse}
status=0
for c in $cases; do
    case "$c" in
        adopt|refuse) if "case_$c"; then echo "PASS $c"; else echo "FAIL $c"; status=1; fi ;;
        *) die "unknown case: $c (adopt, refuse)" ;;
    esac
done
exit "$status"
