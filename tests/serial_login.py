#!/usr/bin/env python3
"""Log in on the installed system's serial console and run a few checks.

Usage:
    python3 tests/serial_login.py [user] [password]

The QEMU instance has to export its serial port as
`-serial unix:/tmp/installed-serial.sock,server=on,nowait`; the transcript
is written to build/installed-serial.log.  Exit status is 0 only if the
login prompt, password prompt, a shell prompt and the requested commands
all appear.
"""
import os
import re
import socket
import sys
import time

SOCK = "/tmp/installed-serial.sock"
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "installed-serial.log")
USER = sys.argv[1] if len(sys.argv) > 1 else "admin"
PASSWORD = sys.argv[2] if len(sys.argv) > 2 else "test-only"
COMMANDS = (
    "id; uname -r; systemctl is-system-running; "
    "swapon --show; systemctl --failed --no-pager --no-legend; echo CHECKS-END"
)
CLEAN = (
    (re.compile(rb"\x1b\][^\x07\x1b]*(\x07|\x1b\\)"), b""),
    (re.compile(rb"\x1b\[[0-9;?]*[A-Za-z]"), b""),
)


def clean(data: bytes) -> bytes:
    for pattern, repl in CLEAN:
        data = pattern.sub(repl, data)
    return data


def connect():
    for _ in range(60):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(SOCK)
            sock.settimeout(1.0)
            return sock
        except OSError:
            time.sleep(0.5)
    raise SystemExit("serial socket never appeared")


def wait_for(sock, needle, timeout, transcript):
    buf = b""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            data = sock.recv(65536)
        except socket.timeout:
            continue
        if not data:
            return None, buf
        transcript.write(data)
        transcript.flush()
        buf += data
        if needle in clean(buf):
            return buf, buf
    return None, buf


def main():
    sock = connect()
    with open(LOG, "wb") as transcript:
        _, _ = wait_for(sock, b"login:", 240, transcript)
        sock.sendall(USER.encode() + b"\n")
        _, _ = wait_for(sock, b"Password:", 60, transcript)
        sock.sendall(PASSWORD.encode() + b"\n")
        prompt, _ = wait_for(sock, b":~$", 60, transcript)
        if prompt is None:
            prompt, _ = wait_for(sock, b"Login incorrect", 5, transcript)
            print("login failed")
            return 1
        sock.sendall(COMMANDS.encode() + b"\n")
        output, _ = wait_for(sock, b"CHECKS-END", 45, transcript)
        if output is None:
            print("checks did not finish")
            return 1

    text = clean(open(LOG, "rb").read()).decode("utf-8", "replace")
    start = text.find("CHECKS-END")
    print(text[max(0, start - 1200):start + 12])
    return 0


if __name__ == "__main__":
    sys.exit(main())
