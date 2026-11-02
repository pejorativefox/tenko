# tea ships as a single static Go binary.  It is not stripped here so the
# payload is preserved exactly as released.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       tea
Version:    0.14.2
Release:    1
Summary:    Command line tool to interact with Gitea (official static binary)
License:    MIT
URL:        https://gitea.com/gitea/tea
Source0:    tea-0.14.2-linux-amd64

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

# make-ca is the CA trust package Browneye ships (it owns /etc/ssl/certs);
# tea talks HTTPS to the Gitea server from its own Go TLS stack.
Requires: make-ca

%description
tea is the official command line tool to interact with Gitea servers:
issues, pulls, organizations, releases and notifications from the terminal.
This package installs the official linux-amd64 release binary, which is
statically linked and therefore has no glibc runtime requirement.

tea is not part of LFS/BLFS.  The user explicitly requested packaging the
official prebuilt binary as an exception to the Browneye version-parity
rule.

The upstream release contains only the executable and no license file; the
MIT license is recorded in this spec.

%prep

%build

%install
rm -rf %{buildroot}
install -D -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/tea

%files
%{_bindir}/tea

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.14.2
- Package the official tea 0.14.2 linux-amd64 release binary
- Binary RPM; tea is not in LFS/BLFS (user-requested exception)
