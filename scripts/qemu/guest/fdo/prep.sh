#!/bin/sh
# Runs before lightdm: create the test account, mount the host share once,
# and get the first-boot policy out of the way.  Ownership is repaired here
# because the fake-root image build flattens non-root ownership.
set -u
. /etc/fdo-verify.env

mkdir -p /mnt /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix || true

# The installroot transaction can run before every schema is present, and
# the glib file trigger cannot compile schemas without a mounted /proc.
# Recompile after the package set is complete so the portal backend can read
# org.gnome.desktop.lockdown and friends.
if [ -x /usr/bin/glib-compile-schemas ]; then
    /usr/bin/glib-compile-schemas /usr/share/glib-2.0/schemas || true
fi
rm -f /tmp/.X0-lock /tmp/.X11-unix/X0
if ! grep -q '^host0 /mnt ' /proc/mounts 2>/dev/null; then
    modprobe 9pnet_virtio >/dev/null 2>&1 || true
    mount -t 9p -o trans=virtio,version=9p2000.L host0 /mnt \
        || echo "fdo-prep: could not mount the host share" >&2
fi

# The login account is created here, as real root, so its home directory has
# the correct owner and the stock /etc/skel files.
/usr/bin/systemd-sysusers >/dev/null 2>&1 || true
if ! getent passwd "$TEST_USER" >/dev/null 2>&1; then
    /usr/sbin/useradd -m -U -c "Desktop verification" -s /bin/bash "$TEST_USER" \
        || exit 1
fi
printf '%s:%s\n' "$TEST_USER" "$TEST_PASSWORD" | /usr/sbin/chpasswd || exit 1
chown -R "$TEST_USER:$TEST_USER" "/home/$TEST_USER" || exit 1
chmod 0700 "/home/$TEST_USER"

# tenko-firstboot is ordered before display-manager.service.  This image has
# an autologin test account and no console user, so record that the root
# password step was deliberately skipped instead of blocking on tty1.
mkdir -p /var/lib/tenko
printf 'skipped by tenko qemu fdo on %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    > /var/lib/tenko/firstboot-root-password.done

echo "fdo-prep: ok" > /mnt/fdo-prep.txt
