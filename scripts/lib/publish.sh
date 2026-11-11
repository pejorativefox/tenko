# Publish targets.  Source after lib/common.sh.
#
# Every publish goes to both the public R2 bucket and the LAN mirror (see
# AGENTS.md).  MIRROR=0 skips the mirror and is only for deliberate
# local-only tests; DRY_RUN=1 stages everything and uploads nothing.

# Cloudflare R2 bucket served at PUBLIC_URL (lib/common.sh).
R2=${R2:-r2_tenko:tenko}
# LAN mirror: ssh target and its web root, served at MIRROR_URL.
MIRROR=${MIRROR:-daspork@192.168.31.9}
MIRROR_PUBLIC=${MIRROR_PUBLIC:-public_html/tenko}
DRY_RUN=${DRY_RUN:-0}

# Repository layout shared by `publish rpm` and `publish repo`.
REPO_ID=tenko-$TENKO_RELEASE
REPO_PATH=packages/$TENKO_RELEASE
URL=${URL:-$PUBLIC_URL/$REPO_PATH/}

rclone_put() {
    rclone copyto "$1" "$R2/$2" --s3-no-check-bucket
}

mirror_enabled() {
    [ "$MIRROR" != 0 ]
}

# mirror_mkdir DIR: create DIR under the mirror web root.
mirror_mkdir() {
    ssh "$MIRROR" "mkdir -p $MIRROR_PUBLIC/$1"
}

# publish_files DIR FILE...: upload FILEs to DIR on R2 and the mirror.
publish_files() {
    local dir=$1 f
    shift
    if [ "$DRY_RUN" = 1 ]; then
        echo "dry run: would upload to $R2/$dir/:"
        mirror_enabled && echo "  and $MIRROR:$MIRROR_PUBLIC/$dir/:"
        printf '  %s\n' "$@"
        return 0
    fi
    echo "uploading to $R2/$dir/"
    for f in "$@"; do
        rclone_put "$f" "$dir/$(basename "$f")"
    done
    if mirror_enabled; then
        echo "mirroring to $MIRROR:$MIRROR_PUBLIC/$dir/"
        mirror_mkdir "$dir"
        rsync -av --partial -e ssh "$@" "$MIRROR:$MIRROR_PUBLIC/$dir/"
    fi
}
