# Setting up a build host

A build host is an installed Tenko system that builds packages, images and
ISOs and publishes them.  Everything runs in rootless podman containers;
the host itself only needs the tools below and some disk space.

## 1. Packages

```sh
sudo dnf install tenko-osdev
```

`tenko-osdev` pulls in the base system with the development environment
(`tenko-base` → `tenko-base-build` → `tenko-buildroot`), podman, the
publish clients (`rclone`, `rsync`, `openssh`), git, curl/wget, the ISO
tools and QEMU with OVMF for boot tests.  See the metapackage layering in
[build.md](build.md#metapackage-layering).

## 2. Rootless podman

Your user needs subordinate UID/GID ranges:

```sh
grep "^$USER:" /etc/subuid /etc/subgid
# if either is missing:
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 "$USER"
podman system migrate
```

## 3. The repository

```sh
git clone ssh://daspork@ssh.pjfox.xyz:2222/daspork/tenko.git
cd tenko
./tenko help
```

Work happens in git worktrees under `.worktrees/` (see
[AGENTS.md](../AGENTS.md)).  The download caches live in the main
checkout's `build/` and every worktree shares them.

## 4. First build

```sh
./tenko sync                  # mirror the published repo into build/cache/repo (~3 GiB)
./tenko image build           # full build image, localhost/tenko/build:r6
./tenko image build --strict  # toolchain buildroot, localhost/tenko/buildroot:r6
./tenko build bc              # build one package
./tenko check                 # unit tests and static checks
```

`tenko build` runs the sync and image steps itself when they are needed,
so the explicit calls only show what happens on a fresh host.  The LAN
mirror is tried before the public site.  Plan for at least 10 GiB of free
space: the mirror (~3 GiB), the two images (~2 GiB), source tarballs and
build output.

## 5. Publishing credentials

Only needed on a host that publishes (see
[build.md](build.md#publishing)):

- **R2 bucket:** an rclone remote named `r2_tenko` (Cloudflare R2, S3
  provider) in `~/.config/rclone/rclone.conf` with write access to the
  `tenko` bucket.  Check it with `rclone lsf r2_tenko:tenko/packages/6/ |
  head`.
- **LAN mirror:** passwordless SSH to `daspork@192.168.31.9` (key-based):
  `ssh daspork@192.168.31.9 true`.
- **Issue tracker:** `tea login add` for <https://pjfox.xyz/git> (login
  name `pjfox.xyz`), used for `tea issues ...` as described in
  [AGENTS.md](../AGENTS.md).

Run `DRY_RUN=1 ./tenko publish rpm some.rpm` to check a publish setup
without uploading.

## Headless and remote hosts

systemd-logind stops a user's processes when their last session ends.  A
long build started over SSH on a remote host therefore dies when the SSH
connection closes, even under `nohup`, `setsid` or tmux.  Either keep the
session open for the duration of the build, or enable lingering once (as
an administrator) so the user's processes survive logout:

```sh
sudo loginctl enable-linger "$USER"
```

Builds run with the network off, so a host only needs network access for
`tenko sync`, source downloads and publishing.  When a host cannot reach a
source site, fetch the tarball on another machine with `./tenko fetch
<package>` and copy it into that host's `build/sources/`; it is verified by
md5 like any other download.
