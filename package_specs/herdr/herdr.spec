# herdr ships as a single static-PIE binary.  It is not stripped here so the
# payload is preserved exactly as released.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       herdr
Version:    0.9.5
Release:    1
Summary:    Terminal workspace and agent multiplexer (official static binary)
License:    Apache-2.0
URL:        https://herdr.dev
Source0:    herdr-0.9.5-linux-x86_64

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

# make-ca is the CA trust package Tenko ships (it owns /etc/ssl/certs).
Requires: git
Requires: make-ca
Requires: bash

%description
Herdr is a terminal workspace and agent multiplexer, split into workspaces,
tabs and panes with persistent sessions.  This package installs the official
linux-x86_64 release binary, which is statically linked and therefore has no
glibc runtime requirement.

Neither herdr nor its components are part of LFS/BLFS.  The user explicitly
approved packaging the official prebuilt binary as an exception to the
Tenko version-parity rule.

The upstream release contains only the executable and no license file; the
Apache-2.0 license is recorded in this spec.

%prep

%build

%install
rm -rf %{buildroot}
install -D -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/herdr

%files
%{_bindir}/herdr

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.9.5
- Package the official herdr 0.9.5 linux-x86_64 release binary
- Binary RPM; herdr is not in LFS/BLFS (user-approved exception)
