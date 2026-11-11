Name:       edk2-ovmf
Version:    202608
Release:    2
Summary:    UEFI firmware for QEMU (OVMF)
License:    BSD-2-Clause-Patent AND Apache-2.0 AND MIT AND BSD-2-Clause AND BSD-3-Clause
URL:        https://github.com/tianocore/edk2
Source0:    edk2-stable202608.tar.gz
Source1:    openssl-3.5.7.tar.gz
Source2:    brotli-e230f474.tar.gz
Source3:    mipi-sys-t-370b5944.tar.gz
Source4:    pylibfdt-cfff8054.tar.gz
Source5:    oniguruma-4ef89209.tar.gz
Source6:    mbedtls-0bebf8b8.tar.gz
Source7:    libspdm-f55cf6d4.tar.gz
Prefix:     /usr

# Build dependencies (not expressed as BuildRequires: the distro folds
# headers into the runtime packages):
#   gcc, g++, make, python3, nasm, acpica (for iasl)
#
# EDK2 references several git submodules from its .dec files even when the
# driver that needs them is not built, so the pinned commits are shipped as
# separate sources and unpacked into the matching paths below.
BuildRequires: nasm

%description
OVMF is the Open Virtual Machine Firmware build of EDK2, providing a UEFI
implementation for QEMU/KVM guests.  It installs the code and variable
store images used by QEMU's pflash interface under /usr/share/edk2/ovmf.
QEMU ships its own bundled edk2 firmware at /usr/share/qemu/edk2-*.fd;
this package does not replace those files, so both packages can be
installed together.  Point QEMU at /usr/share/edk2/ovmf/OVMF_CODE.fd
when the newer EDK2 build is wanted.

%prep
%setup -q -n edk2-edk2-stable202608

mkdir -p CryptoPkg/Library/OpensslLib/openssl
mkdir -p BaseTools/Source/C/BrotliCompress/brotli
mkdir -p MdeModulePkg/Library/BrotliCustomDecompressLib/brotli
mkdir -p MdePkg/Library/MipiSysTLib/mipisyst
mkdir -p MdePkg/Library/BaseFdtLib/libfdt
mkdir -p MdeModulePkg/Universal/RegularExpressionDxe/oniguruma
mkdir -p CryptoPkg/Library/MbedTlsLib/mbedtls
mkdir -p SecurityPkg/DeviceSecurity/SpdmLib/libspdm

tar -xf %{SOURCE1} -C CryptoPkg/Library/OpensslLib/openssl --strip-components=1
tar -xf %{SOURCE2} -C BaseTools/Source/C/BrotliCompress/brotli --strip-components=1
tar -xf %{SOURCE2} -C MdeModulePkg/Library/BrotliCustomDecompressLib/brotli --strip-components=1
tar -xf %{SOURCE3} -C MdePkg/Library/MipiSysTLib/mipisyst --strip-components=1
tar -xf %{SOURCE4} -C MdePkg/Library/BaseFdtLib/libfdt --strip-components=1
tar -xf %{SOURCE5} -C MdeModulePkg/Universal/RegularExpressionDxe/oniguruma --strip-components=1
tar -xf %{SOURCE6} -C CryptoPkg/Library/MbedTlsLib/mbedtls --strip-components=1
tar -xf %{SOURCE7} -C SecurityPkg/DeviceSecurity/SpdmLib/libspdm --strip-components=1

%build
export WORKSPACE=$PWD
export EDK_TOOLS_PATH=$PWD/BaseTools
export PYTHON_COMMAND=python3
make -C BaseTools %{?_smp_mflags}
. ./edksetup.sh
build -a X64 -t GCC -b RELEASE -p OvmfPkg/OvmfPkgX64.dsc -n %{_smp_build_ncpus}

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_datadir}/edk2/ovmf
install -m 0644 Build/OvmfX64/RELEASE_GCC/FV/OVMF_CODE.fd %{buildroot}%{_datadir}/edk2/ovmf/
install -m 0644 Build/OvmfX64/RELEASE_GCC/FV/OVMF_VARS.fd %{buildroot}%{_datadir}/edk2/ovmf/
install -m 0644 Build/OvmfX64/RELEASE_GCC/FV/OVMF.fd      %{buildroot}%{_datadir}/edk2/ovmf/

%files -f %{_sourcedir}/edk2-ovmf.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 202608-2
- Stop installing /usr/share/qemu/edk2-x86_64-code.fd and
  edk2-x86_64-vars.fd symlinks.  qemu owns those paths with its bundled
  firmware, so installing both packages failed the transaction with a
  file conflict.  OVMF stays available at /usr/share/edk2/ovmf/.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 202608-1
- Not in the base set; latest upstream stable tag
  (edk2-stable202608).  Needed to boot-test the UEFI installer image.
- The pinned submodule commits (OpenSSL 3.5.7, Brotli, MIPI Sys-T,
  libfdt, Oniguruma, Mbed TLS, libspdm) are shipped as separate sources
  and unpacked into the tree, because the .dec files reference them even
  for an OVMF-only build.
- Firmware images come from OvmfPkg/OvmfPkgX64.dsc (RELEASE, GCC).
  License: EDK2 is BSD-2-Clause-Patent; the bundled components keep
  their own licenses (OpenSSL Apache-2.0, Brotli MIT, Oniguruma
  BSD-2-Clause, libspdm BSD-3-Clause, Mbed TLS Apache-2.0).
