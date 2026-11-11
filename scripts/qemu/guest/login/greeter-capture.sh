#!/bin/sh
mkdir -p /mnt
mount -t 9p -o trans=virtio,version=9p2000.L host0 /mnt 2>/dev/null || true
i=0
while [ "$i" -lt 45 ] && [ ! -S /tmp/.X11-unix/X0 ]; do
    sleep 2
    i=$((i + 1))
done
{
    echo "===X-SOCKETS==="; ls -l /tmp/.X11-unix 2>&1
    echo "===LIGHTDM-STATE==="; ls -l /run/lightdm /run/lightdm/root /var/lib/lightdm 2>&1
} > /mnt/greeter-capture.log 2>&1
for auth in /var/lib/lightdm/.Xauthority /run/lightdm/root/:0 /root/.Xauthority; do
    [ -e "$auth" ] || continue
    echo "trying XAUTHORITY=$auth" >> /mnt/greeter-capture.log
    if XAUTHORITY="$auth" DISPLAY=:0 xwd -root -silent -out /mnt/greeter.xwd \
            >> /mnt/greeter-capture.log 2>&1; then
        echo "captured with $auth" >> /mnt/greeter-capture.log
        break
    fi
done
{
    echo "===XORG-LOG==="; tail -100 /var/log/Xorg.0.log 2>&1
    echo "===LIGHTDM-LOG==="; tail -60 /var/log/lightdm/lightdm.log 2>&1
} >> /mnt/greeter-capture.log 2>&1
