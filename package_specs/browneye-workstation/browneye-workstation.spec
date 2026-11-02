Name:       browneye-workstation
Version:    13.1
Release:    3
Summary:    Browneye developer workstation (Node.js, SSH, git, agent tools)
License:    MIT
Prefix:     /usr

Requires:   browneye-base
Requires:   nodejs
Requires:   openssh
Requires:   git
Requires:   make-ca
Requires:   which
Requires:   opencode-bin
Requires:   herdr
Requires:   sudo
Requires:   podman-bin

%description
The Browneye developer workstation: the base system plus Node.js/npm,
OpenSSH (password authentication through Linux-PAM), git, the CA trust
store, which, the opencode and herdr agent tools, and the podman container
engine used by the self-hosted build pipeline.

opencode, herdr and podman are not part of LFS/BLFS; the user explicitly
approved packaging their official prebuilt binaries (D19 and the podman
option A decision).  Node.js 26.13.0 is the approved upstream LTS
exception to the BLFS 26.9.0 pin (D17).

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/browneye
touch %{buildroot}/usr/share/browneye/workstation

%files
/usr/share/browneye/workstation

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-3
- Require podman-bin (podman 6.1.4 static bundle under /opt, user-approved
  non-book exception) for the self-hosted container build pipeline

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-2
- Require sudo for the administrative wheel user

* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-1
- New meta: browneye-base + nodejs, openssh, git, make-ca, which,
  opencode-bin, herdr
