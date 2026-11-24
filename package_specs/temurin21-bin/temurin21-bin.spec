# Official Eclipse Temurin HotSpot JDK, including desktop and diagnostic tools.
%global jdk_build 2
%global java_home /opt/temurin21
%global java_payload %{java_home}-%{version}+%{jdk_build}
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}
%global _binary_payload w6.xzdio

Name:       temurin21-bin
Version:    21.0.13.1
Release:    1
Summary:    Eclipse Temurin Java 21 LTS runtime and development kit
License:    GPL-2.0-only WITH Classpath-exception-2.0
URL:        https://adoptium.net/temurin/
Source0:    OpenJDK21U-jdk_x64_linux_hotspot_%{version}_%{jdk_build}.tar.gz
Source1:    temurin21.sh
Source2:    JavaSmoke.java
Prefix:     /opt
ExclusiveArch: x86_64

# Private JDK libraries must not become system-wide library providers.
# The released ELF dependencies and runtime-loaded libraries are listed here.
AutoProv: no
AutoReq: no
Provides:   java = %{version}
Provides:   java-21 = %{version}
Provides:   java-sdk = %{version}
Provides:   java-sdk-21 = %{version}
Requires:   glibc >= 2.17
Requires:   alsa-lib
Requires:   libx11
Requires:   libxext
Requires:   libxi
Requires:   libxrender
Requires:   libxtst
# Font discovery and a usable default font, including in headless AWT.
Requires:   fontconfig
Requires:   liberation-fonts
# Tenko's managed Java trust store.
Requires:   make-ca
# Optional runtime-loaded desktop integrations; Java has fallback paths.
Recommends: cups
Recommends: gtk3
Recommends: libxcomposite
Recommends: libxinerama
Recommends: libxrandr
Recommends: mesa
Recommends: numactl
Recommends: pipewire

# The offline smoke test renders text and checks Tenko's Java trust store.
BuildRequires: fontconfig
BuildRequires: liberation-fonts
BuildRequires: make-ca

%description
Eclipse Temurin is an OpenJDK distribution from Eclipse Adoptium. This
package contains the full Java 21 LTS HotSpot JDK: the runtime, compiler,
desktop modules, headers, and diagnostic tools.

Java 21 supports both the client and server of All the Mods 10: To the Sky.
This package does not install Minecraft, a modpack, or a server service.

The official upstream binaries live in a versioned directory under /opt,
with /opt/temurin21 as the stable JAVA_HOME and all JDK commands linked into
/usr/bin. Java uses Tenko's managed CA certificates. Login shells receive
JAVA_HOME from /etc/profile.d/temurin21.sh; commands also work without it.

%prep
%setup -q -n jdk-%{version}+%{jdk_build}

%build
# Prebuilt upstream JDK: nothing to compile.

%install
rm -rf %{buildroot}
install -d %{buildroot}%{java_payload} %{buildroot}%{_bindir}
cp -a bin conf include jmods legal lib man NOTICE release \
    %{buildroot}%{java_payload}/
ln -s temurin21-%{version}+%{jdk_build} %{buildroot}%{java_home}

for command in bin/*; do
    test -f "$command" && test -x "$command"
    command=${command##*/}
    ln -s "%{java_home}/bin/$command" "%{buildroot}%{_bindir}/$command"
done

rm -f %{buildroot}%{java_payload}/lib/security/cacerts
ln -s /etc/pki/tls/java/cacerts \
    %{buildroot}%{java_payload}/lib/security/cacerts

install -D -m 0644 %{SOURCE1} \
    %{buildroot}%{_sysconfdir}/profile.d/temurin21.sh

%check
bin/java -version
bin/javac --release 21 -d smoke %{SOURCE2}
bin/java -Djava.awt.headless=true \
    -Djavax.net.ssl.trustStore=/etc/pki/tls/java/cacerts \
    -cp smoke JavaSmoke

%files -f %{_sourcedir}/temurin21-bin.filelist

%changelog
* Tue Nov 24 2026 tenko <build@tenko.invalid> 21.0.13.1-1
- New package outside the base set: official Temurin 21.0.13.1+2,
  latest upstream stable Java 21 update checked 2026-11-24.
- User-approved Java 21 LTS major-version pin for All the Mods 10:
  To the Sky client and server compatibility, rather than a newer JDK major.
- Ship the full binary JDK under /opt with /usr/bin command links,
  JAVA_HOME, desktop support, and Tenko's managed Java CA certificates.
- Check Java 21 compilation, virtual threads, cryptography, trust anchors,
  and headless font rendering without downloading or configuring a server.
