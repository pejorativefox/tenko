Name:       bash-completion
Version:    2.18.0
Release:    1
Summary:    Programmable completion for the bash shell
License:    GPL-2.0-or-later
URL:        https://github.com/scop/bash-completion
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
Requires:   bash

%description
bash-completion is a collection of shell functions that extends bash with
programmable completion for hundreds of commands (dnf, rpm, tar, ssh, git,
systemctl, mount and many more), plus the common scaffolding those
functions share.  The package ships the completion library, the per-command
completion files and an /etc/profile.d snippet that loads the library for
interactive shells when bash detects that no completions have been loaded
yet.

bash-completion is not in LFS or BLFS r13.1 (the books only list it as an
optional dependency); the user approved upstream 2.18.0 as the
version-parity exception.

%prep
%setup -q

%build
%configure --sysconfdir=/etc
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/bash-completion.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.18.0-1
- Update to upstream 2.18.0 (was a 2.10 stub that was never built).
  bash-completion is not in LFS or BLFS r13.1; the user approved this
  upstream release as the version-parity exception.
- Source: https://github.com/scop/bash-completion/releases/download/2.18.0/bash-completion-2.18.0.tar.xz
  md5 aa401f77054a83bd45171a2d628dccb0
  sha256 88bcf85124f77f74f2f2f8bcd16ac4382d807a827ede742a64940c7116aea33f
- Changes from 2.10: many new and fixed completions (dnf, rpm, systemctl,
  podman, git, ssh, tar, etc.), completions moved into a helper library
  (helpers-core) and reduced loading cost, fixes for bash 5.x (nounset,
  GLOBSORT) and a large test-suite update.
- Configure with --sysconfdir=/etc so the profile.d snippet is loaded by
  /etc/profile like the rest of the distro's shell snippets (the 2.10
  stub installed it under /usr/etc, where nothing sources it).
- Files are listed from the installed buildroot; the completion tree is
  large, so a generated static filelist replaces the old directory globs.
