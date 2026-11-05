# .NET ships an official self-contained linux-x64 SDK tarball: the dotnet
# host, the SDK (MSBuild, Roslyn, NuGet, templates, workload manifests), the
# Microsoft.NETCore.App and Microsoft.AspNetCore.App runtimes, the apphost
# packs and the dnx tool.  This is a binary repackage, not a source build.
#
# .NET is not part of LFS/BLFS r13.1, so the version-parity rule in AGENTS.md
# cannot be satisfied from the books.  The user explicitly asked for the
# official 10.0.403 SDK tarball to be packaged, which is the same
# user-approved exception as the other -bin specs.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

# ~610 MiB installed; xz level 6 keeps the RPM near the 230 MiB upstream
# tarball without a large packaging cost.
%global _binary_payload w6.xzdio

Name:       dotnet-bin
Version:    10.0.403
Release:    1
Summary:    .NET SDK and runtimes (official prebuilt linux-x64 tarball)
License:    MIT
URL:        https://dotnet.microsoft.com/
Prefix:     /opt

# 10.0.403 SDK tarball, 240199984 bytes
#   sha256 cd7224fe8e8ba57c15f1601439ff8785a1a72b54ae5c89dd5302a32dcfbddf18
#   md5    9393b4ec8882e1f19420d325ad01c71e  (also in ./sources)
Source0:    dotnet-sdk-%{version}-linux-x64.tar.gz

ExclusiveArch: x86_64

# Prebuilt payload: never let rpm guess provides/requires from the bundled
# native libraries, which live under /opt and include their own copies of
# hostfxr, libcoreclr and friends.  The explicit list below is the real host
# requirement.
AutoProv: no
AutoReq: no

Provides:   dotnet = %{version}-%{release}
Provides:   dotnet-sdk = %{version}-%{release}

# libcoreclr.so needs symbols from glibc 2.27.
Requires:   glibc >= 2.27
# libstdc++.so.6 and libgcc_s.so.1, linked by the host and the runtime.
Requires:   gcc-libs
# System.Globalization.Native.so dlopen()s libicuuc.so/libicui18n.so.
Requires:   icu4c
# System.Security.Cryptography.Native.OpenSsl.so dlopen()s libssl.so/libcrypto.so.
# Tenko 6 ships OpenSSL 4, hence the version override in the profile
# script below.
Requires:   openssl-libs
# System.IO.Compression.Native.so dlopen()s libz.so.1.
Requires:   zlib
# TimeZoneInfo reads /usr/share/zoneinfo.
Requires:   tzdb
# /etc/ssl/certs for the default TLS trust store.
Requires:   make-ca
# /usr/bin/dnx is a POSIX sh script.
Requires:   bash

%description
.NET is a free, cross-platform, open-source developer platform for building
many types of applications.

This package repackages the official .NET 10.0.403 SDK linux-x64 tarball
under /opt/dotnet-10.0.403 (with /opt/dotnet as a stable symlink and
/usr/bin/dotnet and /usr/bin/dnx as the PATH entry points).  It contains the
SDK, MSBuild, the Microsoft.NETCore.App and Microsoft.AspNetCore.App 10.0.14
runtimes, the apphost packs, the workload manifests and the bundled
templates.

.NET is not part of LFS/BLFS.  The user explicitly approved packaging the
official prebuilt SDK tarball as an exception to the Tenko 6 version-parity
rule.

The runtime looks for libssl.so.3, but Tenko 6 ships OpenSSL 4, so
/etc/profile.d/dotnet.sh sets DOTNET_OPENSSL_VERSION_OVERRIDE=4.  Kerberos
(GSSAPI) support and libgdiplus are not packaged and are not required for
the CLI or for HTTPS.

%prep
%setup -q -c -n %{name}-%{version}

%build
# Prebuilt payload: nothing to compile.

%install
rm -rf %{buildroot}

install -d %{buildroot}/opt/dotnet-%{version}
cp -a dotnet dnx host packs sdk sdk-manifests shared templates \
    LICENSE.txt ThirdPartyNotices.txt %{buildroot}/opt/dotnet-%{version}/
ln -s dotnet-%{version} %{buildroot}/opt/dotnet

install -d %{buildroot}%{_bindir}
ln -s /opt/dotnet/dotnet %{buildroot}%{_bindir}/dotnet
ln -s /opt/dotnet/dnx %{buildroot}%{_bindir}/dnx

# Framework-dependent apphosts use this to find the shared runtime when they
# are not run through `dotnet`.
install -d %{buildroot}%{_sysconfdir}/dotnet
echo /opt/dotnet > %{buildroot}%{_sysconfdir}/dotnet/install_location

install -d %{buildroot}%{_sysconfdir}/profile.d
cat > %{buildroot}%{_sysconfdir}/profile.d/dotnet.sh << "EOF"
export DOTNET_ROOT=/opt/dotnet
export PATH="$PATH:/opt/dotnet"
# Tenko 6 ships OpenSSL 4; the SDK otherwise only probes libssl.so.3.
export DOTNET_OPENSSL_VERSION_OVERRIDE=4
EOF

%files
%dir /opt/dotnet-%{version}
%license /opt/dotnet-%{version}/LICENSE.txt
/opt/dotnet-%{version}/ThirdPartyNotices.txt
/opt/dotnet-%{version}/dotnet
/opt/dotnet-%{version}/dnx
/opt/dotnet-%{version}/host
/opt/dotnet-%{version}/packs
/opt/dotnet-%{version}/sdk
/opt/dotnet-%{version}/sdk-manifests
/opt/dotnet-%{version}/shared
/opt/dotnet-%{version}/templates
/opt/dotnet
%{_bindir}/dotnet
%{_bindir}/dnx
%dir %{_sysconfdir}/dotnet
%{_sysconfdir}/dotnet/install_location
%{_sysconfdir}/profile.d/dotnet.sh

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 10.0.403-1
- New package: the official .NET 10.0.403 SDK linux-x64 tarball under
  /opt/dotnet-10.0.403, with /opt/dotnet, /usr/bin/dotnet and /usr/bin/dnx
  symlinks, /etc/dotnet/install_location and /etc/profile.d/dotnet.sh.
- .NET is not in LFS/BLFS (user-approved prebuilt exception).
- The SDK only probes libssl.so.3 and Tenko 6 ships OpenSSL 4, so the
  profile script sets DOTNET_OPENSSL_VERSION_OVERRIDE=4.
