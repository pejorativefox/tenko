Name:       gpu-screen-recorder
Version:    6.1.7
Release:    1
Summary:    GPU-accelerated screen recorder for Linux
License:    GPL-3.0-only
URL:        https://git.dec05eba.com/gpu-screen-recorder/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: meson
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: gcc
BuildRequires: ffmpeg
BuildRequires: libva
BuildRequires: libdrm
BuildRequires: libcap
BuildRequires: dbus-libs
BuildRequires: pulseaudio
BuildRequires: wayland
BuildRequires: pipewire
BuildRequires: libx11
BuildRequires: libxcomposite
BuildRequires: libxdamage
BuildRequires: libxfixes
BuildRequires: libxrandr
BuildRequires: vulkan-headers
BuildRequires: xorgproto
BuildRequires: dbus-daemon
BuildRequires: libXdmcp
BuildRequires: libpciaccess
BuildRequires: libxau
BuildRequires: libxcb
BuildRequires: libxext
BuildRequires: libxrender

# gpu-screen-recorder selects the FFmpeg h264_vaapi/hevc_vaapi encoders and
# the Mesa VA driver at runtime; the old packages have neither.  libjpeg-turbo
# is dlopen()ed for JPEG screenshots and MJPEG camera capture and is invisible
# to the automatic requires generator.
Requires:   ffmpeg >= 9.0.2-3
Requires:   mesa >= 26.2.3-8
Requires:   libcap
Requires:   libjpeg-turbo

%description
GPU Screen Recorder records the screen using the GPU for capture and
encoding, keeping CPU usage low.  It can record the desktop, a window or a
single monitor, record audio only, take screenshots, stream, and keep a
ShadowPlay-like replay buffer.

This is the command-line recorder, with the gsr-cli IPC client and the
gsr-kms-server helper.  It uses VA-API through FFmpeg on AMD and Intel GPUs
and the libx264 CPU fallback.  X11 and Wayland capture, xdg-desktop-portal
capture and per-application audio capture are enabled.  NVENC is not built
because Tenko does not ship the NVIDIA driver stack.

%prep
%setup -q -c -n %{name}-%{version}

%build
# FFmpeg's configure installs its pkg-config files in /usr/lib/pkgconfig
# and its shared libraries in /usr/lib, which is not in pkgconf's or the
# 64-bit linker's default search path on this distro.
export PKG_CONFIG_PATH=/usr/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}
export LDFLAGS="-L/usr/lib -Wl,-rpath-link,/usr/lib${LDFLAGS:+ $LDFLAGS}"
mkdir build
pushd build
meson setup ..                    \
    --prefix=/usr                 \
    --buildtype=release           \
    -Dsystemd=true                \
    -Dcapabilities=false          \
    -Dnvidia_suspend_fix=true     \
    -Dportal=true                 \
    -Dapp_audio=true              \
    -Dplugin_examples=false       \
    -Dffmpeg_static=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%post
# Tenko's rpm is built without file-capability support, so %caps cannot be
# used.  Apply the capability after installation instead; without it GSR
# falls back to pkexec and asks for authentication on monitor capture.
if [ -x /usr/sbin/setcap ]; then
    /usr/sbin/setcap cap_sys_admin+ep /usr/bin/gsr-kms-server ||
        echo "warning: could not set cap_sys_admin on gsr-kms-server; monitor capture will ask for authentication" >&2
fi

%files -f %{_sourcedir}/gpu-screen-recorder.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 6.1.7-1
- New package: gpu-screen-recorder 6.1.7, the latest stable upstream tag.
  CLI recorder, gsr-cli and gsr-kms-server built with VA-API through
  FFmpeg 9.0.2-3 and Mesa 26.2.3-8, plus the libx264 CPU fallback.
  xdg-desktop-portal capture and per-application audio are enabled, and
  the %post script applies cap_sys_admin to gsr-kms-server so monitor
  capture does not prompt for a password.  Tenko's rpm is built without
  file-capability support, so the capability is set with setcap at install
  time rather than with %caps.  The systemd user service, the NVIDIA
  suspend workaround modprobe file and the upstream helper scripts are
  installed.  NVENC is not built: Tenko ships no NVIDIA driver stack, so
  the package uses the VA-API and CPU paths.
