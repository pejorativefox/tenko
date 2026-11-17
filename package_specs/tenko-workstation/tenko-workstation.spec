Name:       tenko-workstation
Version:    6
Release:    3
Epoch:      1
Summary:    Tenko developer workstation (Node.js, SSH, git, containers)
License:    MIT
URL:        https://github.com/pejorativefox/tenko
Prefix:     /usr

Requires:   tenko-base
Requires:   nodejs
Requires:   openssh
Requires:   git
Requires:   make-ca
Requires:   which
Requires:   sudo
Requires:   podman

%description
The Tenko developer workstation: the base system plus Node.js/npm,
OpenSSH (password authentication through Linux-PAM), git, the CA trust
store, which, and the podman container engine used by the self-hosted
build pipeline.

podman is not part of the base set and is built from source.  Node.js
26.13.0 is the approved upstream LTS exception to the pinned 26.9.0
version (D17).

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/tenko
touch %{buildroot}/usr/share/tenko/workstation

%files -f %{_sourcedir}/tenko-workstation.filelist

%changelog
* Tue Nov 17 2026 tenko <build@tenko.invalid> 6-3
- Drop the opencode-bin and herdr requirements: those prebuilt-binary
  packages are no longer part of the distribution.

* Sat Nov 14 2026 tenko <build@tenko.invalid> 6-2
- Require podman, built from source, instead of the podman-bin static
  bundle (podman obsoletes podman-bin, so existing installs upgrade).

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-1
- Rebase on the Tenko 6 distro release with Epoch 1 so installs carrying
  the old 13.1 EVR upgrade cleanly.
- Drop the browneye-workstation Obsoletes/Provides alias and the old
  marker cleanup; no Browneye installs remain.

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
