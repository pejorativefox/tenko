# The kernel's firmware loader searches /lib/firmware, which is
# /usr/lib/firmware on this usrmerged system.  The raw SOF images are ELF
# containers, so strip and automatic dependency generation must stay off or
# rpmbuild would corrupt them.
%global debug_package %{nil}
%global __strip /bin/true
%global __spec_install_post %{nil}

Name:       sof-firmware
Version:    2026.09.2
Release:    1
Summary:    Sound Open Firmware for Intel audio DSPs
License:    BSD-3-Clause
URL:        https://github.com/thesofproject/sof-bin
Source0:    sof-bin-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch

AutoProv:   no
AutoReq:    no

# BuildRequires: none (toolchain only)

%description
Sound Open Firmware is the firmware that runs on the audio DSP found in
Intel laptops and desktops from Broadwell onwards.  The kernel's
sof-audio-pci drivers load these images and the matching topology files
before the ALSA sound card can be registered; without them the DSP probe
fails and the machine has no audio device at all.

This package installs the signed Intel firmware (and the community-built
fallback images) plus the IPC3 and IPC4 topology files under
/usr/lib/firmware/intel.  It is required on hardware where the HDA
controller binds to the SOF driver; machines that use snd_hda_intel
directly need only alsa-ucm-conf.

%prep
%setup -q -n sof-bin-%{version}

%build
# Firmware binaries: nothing to compile.

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_prefix}/lib/firmware/intel
cp -a sof sof-tplg sof-ipc4 sof-ipc4-tplg sof-ipc4-lib \
    %{buildroot}%{_prefix}/lib/firmware/intel/
ln -s sof-ipc4-tplg %{buildroot}%{_prefix}/lib/firmware/intel/sof-ace-tplg

install -d %{buildroot}%{_datadir}/licenses/%{name}
install -m 0644 LICENCE.Intel LICENCE.NXP Notice.NXP README.Intel \
    %{buildroot}%{_datadir}/licenses/%{name}/

%files -f %{_sourcedir}/sof-firmware.filelist

%changelog
* Thu Nov 19 2026 tenko <build@tenko.invalid> 2026.09.2-1
- New package, not in the base set: latest upstream stable release
  (sof-bin v2026.09.2, checked 2026-11-19).  Intel moved the SOF firmware
  out of linux-firmware, so the Tenko kernel's sof-audio-pci drivers had no
  firmware to load and Intel SOF machines registered no sound card.
