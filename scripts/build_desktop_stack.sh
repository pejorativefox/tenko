#!/usr/bin/env bash
# Build the X/GNOME desktop chain inside the self-hosted base image.
# One persistent container so installed dependencies are visible to the next
# package; each RPM is also kept under build/desktop-parity-<date>/build/<pkg>.
#
# PHASE=core  X libraries, GLib/GI, cairo, GTK2/GTK3 (default)
# PHASE=rest  CMake, libjpeg-turbo, ImageMagick, LLVM
# PHASE=xfce-deps  XFCE 4.20 dependencies
# PHASE=xfce  the XFCE 4.20 core desktop (X11 only)
# PHASE=desktop  Xorg server, input/video drivers, xinit, fonts (X11 only)
# PHASE=net     libpcap, nmap/ncat/nping and passt/pasta (podman networking)
# PHASE=proxy   privoxy and proxychains-ng (not in the base set; approved exceptions)
set -uo pipefail
cd "$(dirname "$0")/.."
. scripts/repo_tools.sh

IMG=${IMG:-$(pick_image localhost/tenko/base:r6 localhost/tenko/base:r13.1)}
OUT=${OUT:-$PWD/build/desktop-parity-$(date +%Y%m%d)}
JOBS=${JOBS:-8}
PHASE=${PHASE:-core}
KEEP=${KEEP:-0}

mkdir -p "$OUT"/{logs,status,build}
if [ "$KEEP" != "1" ]; then
    podman rm -f tenko-desktop >/dev/null 2>&1 || true
fi
if ! podman container exists tenko-desktop; then
    podman run -d --name tenko-desktop --network=none \
        -v "$PWD/package_specs:/specs:ro,z" \
        -v "$HOME/rpmbuild/SOURCES:/sources:ro,z" \
        -v "$OUT:/out:rw,z" \
        "$IMG" sleep infinity >/dev/null
fi

build() {
    local name=$1 top=$2
    shift 2
    if grep -q '^ok ' "$OUT/status/$top" 2>/dev/null; then
        echo "skip $top"
        return 0
    fi
    mkdir -p "$OUT/build/$top"/{BUILD,BUILDROOT,RPMS,SRPMS,SPECS}
    if podman exec tenko-desktop rpmbuild -bb --nodeps \
            --define "_topdir /out/build/$top" \
            --define "_sourcedir /sources" \
            --define "_smp_mflags -j$JOBS" \
            "$@" "/specs/$name/$name.spec" > "$OUT/logs/$top.log" 2>&1; then
        podman exec tenko-desktop bash -lc \
            "rpm -Uvh --nodeps --replacepkgs --replacefiles /out/build/$top/RPMS/x86_64/*.rpm" \
            >> "$OUT/logs/$top.log" 2>&1
        echo "ok $top $(date +%T)" | tee "$OUT/status/$top"
    else
        echo "fail $top $(date +%T)" | tee "$OUT/status/$top"
        return 1
    fi
}

if [ "$PHASE" = "core" ]; then
    ORDER="xorgproto xtrans xcb-proto libxau libxdmcp libxcb libx11
libxext libxrender libxfixes libxi libxcursor libxrandr libxinerama
libxcomposite libxdamage libxxf86vm libxtst pixman libpng
freetype fontconfig libxft fribidi"

    for p in $ORDER; do
        build "$p" "$p" || exit 1
    done

    # glib-pass1 (the no-introspection stage-1 glib) was removed
    # 2026-11-03; a from-scratch stack build now needs glib present in the
    # build image.
    build gobject-introspection gobject-introspection || exit 1
    build glib glib || exit 1

    for p in harfbuzz cairo libxml2 at-spi2-core shared-mime-info gdk-pixbuf pango libepoxy \
             libxkbcommon gtk3 vte; do
        build "$p" "$p" || exit 1
    done
elif [ "$PHASE" = "rest" ]; then
    for p in curl libuv cmake libjpeg-turbo imagemagick llvm; do
        build "$p" "$p" || exit 1
    done
elif [ "$PHASE" = "xfce-deps" ]; then
    for p in xcb-util libice libsm libxres libxkbfile hwdata libdisplay-info \
             iso-codes libogg libvorbis libgudev libnotify libusb upower duktape \
             polkit startup-notification libwnck libxklavier libcanberra \
             desktop-file-utils libexif libxslt iceauth; do
        build "$p" "$p" || exit 1
    done
elif [ "$PHASE" = "xfce" ]; then
    for p in libxfce4util xfconf libxfce4ui xfce4-terminal exo garcon xfce4-dev-tools \
             libxfce4windowing xfce4-panel xfwm4 xfce4-session xfce4-settings \
             thunar thunar-volman tumbler xfce4-appfinder xfdesktop \
             xfce4-power-manager xfce-polkit; do
        build "$p" "$p" || exit 1
    done
elif [ "$PHASE" = "desktop" ]; then
    for p in util-macros font-util libfontenc mkfontscale encodings \
             libxcvt libtirpc libpciaccess libdrm xkeyboard-config \
             libxfont2 libxt libxmu xkbcomp font-alias font-bh-ttf dbus xorg-server xinit xauth \
             libevdev mtdev libinput xf86-input-libinput \
             xf86-video-vesa \
             xrdb xset xmodmap xhost xwininfo xwd hicolor-icon-theme \
             xdg-desktop-portal xdg-desktop-portal-gtk \
             tenko-desktop-config xfce-desktop; do
        build "$p" "$p" || exit 1
    done
elif [ "$PHASE" = "net" ]; then
    for p in libpcap nmap passt; do
        build "$p" "$p" || exit 1
    done
elif [ "$PHASE" = "proxy" ]; then
    for p in privoxy proxychains-ng; do
        build "$p" "$p" || exit 1
    done
fi

echo "phase $PHASE done"
