# QEMU test helpers.  Source after lib/common.sh.
#
#   test_rootfs ROOTFS SET [PKG...]  install the installer's package SET
#                                    (desktop or base) plus PKGs into ROOTFS,
#                                    with scriptlets; reused while the
#                                    repository and the package list match
#   disk_image ROOTFS IMG [SIZE]     write an ext4 image of ROOTFS
#   qemu_start ROOTFS IMG [ARGS...]  boot IMG with ROOTFS's kernel in the
#                                    background (direct kernel boot, serial to
#                                    SERIAL, monitor on MON); sets QEMU_PID
#   qemu_wait_serial REGEX SECONDS   wait until the serial log matches
#   qemu_stop                        quit QEMU and wait for it
#   mon COMMAND                      run a QEMU monitor command
#   screendump OUT.png               capture the VGA output
#   sendkeys TEXT                    type TEXT and Enter on the guest console
#
# Settings (environment): REPO (default: the offline mirror, synced unless
# OFFLINE=1), MEM (3072), SMP (4), VNC (127.0.0.1:1), SERIAL, MON, SHARE
# (a 9p share mounted by the guest as host0), APPEND (extra kernel
# arguments).

REPO=${REPO:-}
OFFLINE=${OFFLINE:-0}
MEM=${MEM:-3072}
SMP=${SMP:-4}
VNC=${VNC:-127.0.0.1:1}
APPEND=${APPEND:-}
QEMU_PID=

# The repository test roots install from: the offline mirror by default.
qemu_repo() {
    if [ -n "$REPO" ]; then
        printf '%s\n' "$REPO"
        return
    fi
    if [ "$OFFLINE" != 1 ]; then
        bash scripts/build/sync.sh >&2
    fi
    [ -f "$TENKO_REPO_CACHE/repodata/repomd.xml" ] ||
        die "no offline mirror in $TENKO_REPO_CACHE; run tenko sync or set REPO"
    printf '%s\n' "$TENKO_REPO_CACHE"
}

# installer_packages SET: the packages tenko-installer installs for SET.
installer_packages() {
    python3 - "$1" <<'PY'
import sys
sys.path.insert(0, "package_specs/tenko-installer/files")
import install
print(" ".join(install.PACKAGE_SETS[sys.argv[1]]))
PY
}

_repo_stamp() {
    local url=$1
    case "$url" in
        file://*) sha256sum "${url#file://}/repodata/repomd.xml" | cut -d' ' -f1 ;;
        *) curl -fsSL --max-time 20 "${url%/}/repodata/repomd.xml" | sha256sum | cut -d' ' -f1 ;;
    esac
}

test_rootfs() {
    local rootfs=$1 set=$2 repo url packages stamp
    shift 2
    repo=$(qemu_repo)
    url=$(repo_url "$repo")
    packages="$(installer_packages "$set") $*"
    stamp="$(_repo_stamp "$url" || true) $(echo $packages | tr ' ' '\n' | sort | tr '\n' ' ')"
    if [ "${REBUILD_ROOTFS:-0}" != 1 ] && [ -f "$rootfs/.tenko-test-rootfs" ] &&
       [ "$(cat "$rootfs/.tenko-test-rootfs")" = "$stamp" ] &&
       [ -f "$rootfs/boot/vmlinuz-$KVER" ]; then
        echo "reusing $rootfs (repository and package list unchanged)"
        return 0
    fi

    echo "installing the $set set into $rootfs from $repo"
    unshare -r rm -rf "$rootfs"
    mkdir -p "$rootfs/dev"
    # Fake root cannot mknod; plain files are enough for the scriptlets.
    for dev in null zero random urandom; do : > "$rootfs/dev/$dev"; done
    local dnf=(unshare -r dnf -y --nogpgcheck --installroot "$rootfs"
               --releasever="$TENKO_RELEASE" --disablerepo='*'
               --repofrompath=tenko,"$url" --setopt=install_weak_deps=False)
    # tenko-basefs creates the merged-/usr symlinks every scriptlet needs.
    "${dnf[@]}" install tenko-basefs
    # shellcheck disable=SC2086  # package list
    "${dnf[@]}" install $packages ||
        echo "warning: dnf reported a scriptlet failure; checking packages" >&2
    local pkg
    for pkg in $packages; do
        rpm -q --root "$rootfs" "$pkg" >/dev/null ||
            die "missing package after install: $pkg"
    done

    # Fake root skips what real root would do at install or first boot.
    local in=(unshare -r chroot "$rootfs")
    "${in[@]}" /usr/bin/systemd-sysusers || true
    "${in[@]}" /usr/bin/systemctl --root=/ preset-all || true
    "${in[@]}" /sbin/ldconfig || true
    "${in[@]}" /usr/sbin/depmod -a "$KVER" || true
    if [ ! -f "$rootfs/boot/initramfs-$KVER.img" ]; then
        bash scripts/image/initramfs.sh "$rootfs" "$KVER"
    fi
    # lightdm's %post cannot chown its state directories under fake root.
    local d
    for d in var/lib/lightdm var/lib/lightdm-data var/cache/lightdm var/log/lightdm; do
        [ -d "$rootfs/$d" ] && chmod -R a+rwX "$rootfs/$d"
    done
    printf '%s\n' "$stamp" > "$rootfs/.tenko-test-rootfs"
}

disk_image() {
    local rootfs=$1 img=$2 size=${3:-6G}
    rm -f "$img"
    truncate -s "$size" "$img"
    unshare -r /usr/sbin/mke2fs -q -t ext4 -d "$rootfs" "$img"
}

qemu_accel() {
    if [ -w /dev/kvm ]; then
        echo "-enable-kvm -cpu host"
    else
        echo "warning: /dev/kvm is not writable; using TCG (slow)" >&2
        echo "-cpu max"
    fi
}

qemu_start() {
    local rootfs=$1 img=$2
    shift 2
    [ -f "$rootfs/boot/vmlinuz-$KVER" ] || die "missing kernel $KVER in $rootfs"
    local initrd=() share=()
    [ -f "$rootfs/boot/initramfs-$KVER.img" ] &&
        initrd=(-initrd "$rootfs/boot/initramfs-$KVER.img")
    if [ -n "${SHARE:-}" ]; then
        mkdir -p "$SHARE"
        share=(-virtfs "local,path=$SHARE,mount_tag=host0,security_model=none")
    fi
    rm -f "$SERIAL" "$MON"
    # shellcheck disable=SC2046  # accel flags
    qemu-system-x86_64 $(qemu_accel) -m "$MEM" -smp "$SMP" \
        -kernel "$rootfs/boot/vmlinuz-$KVER" "${initrd[@]}" \
        -append "root=/dev/vda rw console=ttyS0 loglevel=6 systemd.show_status=1 $APPEND" \
        -drive "file=$img,format=raw,if=virtio" \
        -vga std -display none -vnc "$VNC" \
        -monitor "unix:$MON,server,nowait" \
        -serial "file:$SERIAL" \
        "${share[@]}" -no-reboot "$@" &
    QEMU_PID=$!
    trap qemu_stop EXIT
}

qemu_running() {
    [ -n "$QEMU_PID" ] && kill -0 "$QEMU_PID" 2>/dev/null
}

qemu_wait_serial() {
    local pattern=$1 deadline=$(( $(date +%s) + $2 ))
    while [ "$(date +%s)" -lt "$deadline" ]; do
        grep -qE "$pattern" "$SERIAL" 2>/dev/null && return 0
        qemu_running || return 1
        sleep 2
    done
    return 1
}

mon() {
    [ -S "$MON" ] || return 1
    python3 - "$MON" "$1" <<'PY' || true
import socket, sys
s = socket.socket(socket.AF_UNIX)
s.connect(sys.argv[1])
s.sendall((sys.argv[2] + "\n").encode())
s.settimeout(1)
try:
    while s.recv(4096):
        pass
except OSError:
    pass
PY
}

screendump() {
    local out=$1 ppm=${1%.*}.ppm
    rm -f "$ppm"
    mon "screendump $ppm"
    sleep 2
    [ -s "$ppm" ] || return 1
    if command -v convert >/dev/null 2>&1 && convert "$ppm" "$out" 2>/dev/null; then
        rm -f "$ppm"
        echo "screenshot: $out"
    else
        echo "screenshot: $ppm"
    fi
}

sendkeys() {
    local text=$1 i c
    for ((i = 0; i < ${#text}; i++)); do
        c=${text:i:1}
        case "$c" in
            [a-z0-9]) mon "sendkey $c" ;;
            -) mon "sendkey minus" ;;
            .) mon "sendkey dot" ;;
            ' ') mon "sendkey spc" ;;
            *) die "sendkeys: unsupported character '$c'" ;;
        esac
        sleep 0.15
    done
    mon "sendkey ret"
}

qemu_stop() {
    if qemu_running; then
        mon quit
        sleep 1
        kill "$QEMU_PID" 2>/dev/null || true
        wait "$QEMU_PID" 2>/dev/null || true
    fi
    QEMU_PID=
}
