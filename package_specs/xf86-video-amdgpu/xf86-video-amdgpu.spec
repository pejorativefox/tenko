Name:       xf86-video-amdgpu
Version:    23.0.0
Release:    1
Summary:    Xorg AMDGPU video driver
License:    Historical Permission Notice and Disclaimer
Prefix:     /usr
Source0:    xf86-video-amdgpu-23.0.0.tar.xz

BuildRequires: xorg-server, libdrm, mesa
Requires:   xorg-server

%description
The Xorg video driver for AMD Radeon GPUs (Volcanic Islands and newer) and
AMD APUs. It uses the kernel amdgpu driver and the radeonsi Gallium driver
in Mesa, with glamor acceleration on a server built with glamor enabled.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xf86-video-amdgpu.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 23.0.0-1
- Initial package (BLFS r13.1 archive); replaces the stale 3.30.1 template
  with a static filelist and the current 23.0.0 source
