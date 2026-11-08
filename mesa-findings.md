# GPU acceleration / Chrome findings — Tenko Linux 6

Date: 2026-11-08

## Bottom line

The lack of Chrome GPU acceleration is **not** a Chrome, kernel, or hardware
problem. Both GPUs are detected and their kernel drivers are loaded, but the
Tenko 6 `mesa` package is built with only the software rasterizer (`llvmpipe`)
and the VirtIO guest driver. There are no hardware DRI drivers installed for
either GPU, and there is no system Vulkan loader/ICD.

In short: **the `mesa` package needs to be rebuilt with the hardware Gallium
drivers enabled.** This is a packaging/build-config omission, not something
that can be fixed by installing another package from the current Tenko repo.

## Hardware present

| GPU | PCI ID | Kernel driver | Notes |
|---|---|---|---|
| Intel HD Graphics 4400 (Haswell) | `8086:0a16` | `i915` | Drives the internal eDP panel; this is the GPU Chrome will use |
| AMD Radeon R5 M230 (Hainan, GCN1) | `1002:6664` | `amdgpu` | Hybrid/offload dGPU |

Kernel log confirms both initialized successfully:

- `i915 0000:00:02.0: [drm] Found haswell/ult (device ID 0a16) integrated display version 7.00`
- `amdgpu 0000:05:00.0: [drm] Initialized amdgpu 3.64.0 for 0000:05:00.0 on minor 1`
- Firmware packages including `linux-firmware-intel-gpu` and
  `linux-firmware-amd-gpu` are installed.

## Evidence of the Mesa problem

### Installed Mesa is software-only

`rpm -qi mesa`:

> Open source implementations of OpenGL, OpenGL ES, EGL, GBM, the
> llvmpipe software rasterizer and the virgl guest driver for QEMU's
> virtio-gpu 3D device, built for X11 only (no Wayland, no Vulkan).

Installed version: `mesa-26.2.3-5.x86_64`.

### DRI directory contains no hardware drivers

```
/usr/lib64/dri/
├── kms_swrast_dri.so -> libdril_dri.so
├── libdril_dri.so
├── swrast_dri.so     -> libdril_dri.so
└── virtio_gpu_dri.so -> libdril_dri.so
```

Missing:

- `crocus_dri.so` — Intel Gen4–7.5, including Haswell
- `iris_dri.so` — Intel Gen8+
- `radeonsi_dri.so` — AMD GCN1+, including Hainan
- `r600_dri.so` — older AMD (optional)

### Direct GBM test on the render nodes

Testing with EGL/GBM directly against the GPU render nodes:

```
Intel (/dev/dri/renderD129):
  crocus: driver missing
  RENDERER = llvmpipe (LLVM 23.1.0, 256 bits)

AMD (/dev/dri/renderD130):
  radeonsi: driver missing
  RENDERER = llvmpipe (LLVM 23.1.0, 256 bits)
```

`libgallium-26.2.3.so` contains only stub driver descriptors for
`crocus`/`iris`/`radeonsi`, not the actual driver implementation. Creating the
missing `*_dri.so` symlinks manually would therefore **not** enable hardware
acceleration; the driver code has to be compiled in.

### No Vulkan

- `/usr/share/vulkan/icd.d/` does not exist.
- No system `libvulkan.so.1`.
- Chrome bundles its own `libvulkan.so.1` plus SwiftShader, but with no system
  ICD it reports:

```
Warning: vkCreateInstance: Found no drivers!
Warning: vkCreateInstance failed with VK_ERROR_INCOMPATIBLE_DRIVER
```

This is expected and harmless for GL-based acceleration. It will remain until a
Vulkan loader + hardware ICDs are packaged.

### Xorg is using software GL

From `/var/log/Xorg.0.log`:

```
(==) Matched intel as autoconfigured driver 0
(WW) Warning, couldn't open module intel
...
(II) modeset(0): using drv /dev/dri/card2
(II) AIGLX: Screen 0 is not DRI2 capable
(II) IGLX: Loaded and initialized swrast
(II) GLX: Initialized DRISWRAST GL provider for screen 0
```

The `modesetting` X driver is being used (the optional `xf86-video-intel` DDX
is not installed). That is fine; the missing piece is the Mesa DRI driver, not
the X driver.

## Required fix

Rebuild the `mesa` package with hardware Gallium drivers. For this machine:

```meson
-Dgallium-drivers=swrast,virtio_gpu,crocus,radeonsi
```

For a more general-purpose distro build, consider:

```meson
-Dgallium-drivers=swrast,virtio_gpu,crocus,iris,radeonsi,r600
```

Keep the existing options (`-Dplatforms=x11`, `-Dvulkan-drivers=""`, etc.)
unless Vulkan is being added at the same time.

The package's `%files` already includes `/usr/lib64/dri/`, so the newly built
driver symlinks should be packaged automatically.

### After rebuilding

1. Install the new `mesa` RPM.
2. Log out/in or reboot so Xorg reinitializes glamor/GLX.
3. Verify the driver links exist:

   ```bash
   ls -l /usr/lib64/dri/
   ```

   Expected new entries include `crocus_dri.so` and `radeonsi_dri.so`.

4. Check `chrome://gpu`. It should show hardware acceleration, e.g.:

   ```
   ANGLE (Intel, Mesa Intel(R) HD Graphics 4400 (HSW GT2), OpenGL 4.6)
   ```

5. If Chrome still reports software rendering, check `chrome://gpu` for a
   blocklist entry. Haswell is old enough that a temporary
   `--ignore-gpu-blocklist` test may be useful.

## Optional: Vulkan

Vulkan is not required for Chrome GPU acceleration on this machine. If it is
wanted as well:

- Build Mesa with:
  ```meson
  -Dvulkan-drivers=intel_hasvk,amd
  ```
  - `intel_hasvk` is Mesa's Haswell Vulkan driver.
  - `amd` is RADV, for the Hainan GCN1 GPU.
- Package the Khronos `vulkan-loader` and install the ICD JSON files under
  `/usr/share/vulkan/icd.d/`.

Without the loader + ICD JSON, Chrome's bundled Vulkan loader will continue to
report `Found no drivers!`.

## Notes

- The internal panel is connected to the Intel GPU, so `crocus` is the critical
  driver for Chrome on this laptop. `radeonsi` enables the AMD dGPU for
  offload/other applications.
- Installing `xf86-video-intel` alone will not fix 3D acceleration; it is a
  display driver, not a Mesa DRI driver.
- The `EGL display does not support requested client API 'OpenGL'` warning is a
  downstream symptom of Chrome/ANGLE failing to find a hardware GL adapter. It
  should resolve once `crocus`/`radeonsi` are available.
