# opencode ships as a self-contained Bun-compiled ELF.  The payload contains
# its own JavaScript runtime and modules, so it must not be stripped or
# rewritten.  Override both the tenko strip helper and rpm's brp-strip.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       opencode-bin
Version:    2.2.5
Release:    1
Summary:    AI coding agent CLI (official prebuilt linux-x64 binary)
License:    MIT
URL:        https://opencode.ai
Source0:    opencode-linux-x64-2.2.5.tar.gz

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

Provides: opencode = %{version}-%{release}

# make-ca is the CA trust package Tenko ships (it owns /etc/ssl/certs).
Requires: glibc >= 2.17
Requires: git
Requires: make-ca
Requires: bash

%description
OpenCode is an AI coding agent for the terminal.  This package installs the
official prebuilt linux-x64 release binary, a self-contained Bun-compiled
ELF that needs no Node.js runtime.

Neither opencode nor its components are part of the base set.  The user
explicitly approved packaging the official prebuilt binary as an exception
to the Tenko version-policy rule.

The upstream release tarball contains only the executable and no license
file; the MIT license is recorded in this spec.

%prep
%setup -q -c -n %{name}-%{version}

%build

%install
rm -rf %{buildroot}
install -D -m 0755 opencode %{buildroot}%{_bindir}/opencode

%files
%{_bindir}/opencode

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.2.5
- Package the official opencode 2.2.5 linux-x64 release binary
- Binary RPM; opencode is not in the base set (user-approved exception)
