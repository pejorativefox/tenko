Name:       tenko-workstation
Version:    13.1
Release:    4
# Tenko rename compatibility (issue #22).
Obsoletes: browneye-workstation < 13.1-4
Provides: browneye-workstation = %{version}-%{release}
Summary:    Tenko developer workstation (Node.js, SSH, git, agent tools)
License:    MIT
Prefix:     /usr

Requires:   tenko-base
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
The Tenko developer workstation: the base system plus Node.js/npm,
OpenSSH (password authentication through Linux-PAM), git, the CA trust
store, which, the opencode and herdr agent tools, and the podman container
engine used by the self-hosted build pipeline.

opencode, herdr and podman are not part of the base set; the user explicitly
approved packaging their official prebuilt binaries (D19 and the podman
option A decision).  Node.js 26.13.0 is the approved upstream LTS
exception to the pinned 26.9.0 version (D17).

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/tenko
touch %{buildroot}/usr/share/tenko/workstation

%post
# Remove the old marker directory left by browneye-workstation.
rm -f /usr/share/browneye/workstation
rmdir /usr/share/browneye 2>/dev/null || true

%files
/usr/share/tenko/workstation

%changelog
* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-4
- Rename browneye-workstation to tenko-workstation and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-3
- Require podman-bin (podman 6.1.4 static bundle under /opt, user-approved
  base-set exception) for the self-hosted container build pipeline

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-2
- Require sudo for the administrative wheel user

* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-1
- New meta: browneye-base + nodejs, openssh, git, make-ca, which,
  opencode-bin, herdr
