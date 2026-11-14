Name:       podman
Version:    6.2.0
Release:    1
Summary:    Daemonless container engine for OCI containers and pods
License:    Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND ISC AND MIT AND MPL-2.0
URL:        https://podman.io/
Source0:    %{name}-%{version}.tar.gz
# containers/common at the version podman 6.2.0 vendors (go.podman.io/common
# v0.70.0): the default seccomp profile.
Source1:    container-libs-common-0.70.0.tar.gz
Source2:    containers.conf
Source3:    storage.conf
Source4:    policy.json
Source5:    registries.conf
Prefix:     /usr
ExclusiveArch: x86_64

BuildRequires: go
BuildRequires: go-md2man
BuildRequires: gpgme
BuildRequires: libassuan
BuildRequires: libgpg-error
BuildRequires: libseccomp
BuildRequires: systemd
BuildRequires: shadow
BuildRequires: btrfs-progs
BuildRequires: sqlite
BuildRequires: man-db
BuildRequires: perl

# Go modules are vendored in the release tarball (vendor/modules.txt,
# checked against go.mod); nothing is downloaded during the build.

# Runtime helpers, all in podman's built-in search paths:
# /usr/bin/crun, /usr/libexec/podman/{conmon,netavark,aardvark-dns,catatonit}
# and pasta in $PATH.
Requires:   conmon
Requires:   crun
Requires:   netavark
Requires:   aardvark-dns
Requires:   catatonit
Requires:   pasta
# newuidmap/newgidmap (setuid) for rootless multi-ID mapping
Requires:   shadow
# nsenter, unshare
Requires:   util-linux
# overlays, fuse, netfilter module autoload
Requires:   kmod
# /run/user/$UID and cgroup delegation for the rootless session
Requires:   systemd
# /etc/subuid and /etc/subgid
Requires:   tenko-sysconfig

# Replaces the static third-party bundle.
Obsoletes:  podman-bin < 6.1.4-7
Provides:   podman-bin = %{version}-%{release}

%global podman_make %{__make} \\\
    PREFIX=%{_prefix} \\\
    BINDIR=%{_bindir} \\\
    LIBEXECDIR=%{_libexecdir} \\\
    LIBDIR=%{_prefix}/lib \\\
    MANDIR=%{_mandir} \\\
    ETCDIR=%{_sysconfdir} \\\
    TMPFILESDIR=%{_prefix}/lib/tmpfiles.d \\\
    USERTMPFILESDIR=%{_datadir}/user-tmpfiles.d \\\
    SYSTEMDDIR=%{_prefix}/lib/systemd/system \\\
    USERSYSTEMDDIR=%{_prefix}/lib/systemd/user \\\
    SYSTEMDGENERATORSDIR=%{_prefix}/lib/systemd/system-generators \\\
    USERSYSTEMDGENERATORSDIR=%{_prefix}/lib/systemd/user-generators \\\
    BASHINSTALLDIR=%{_datadir}/bash-completion/completions \\\
    ZSHINSTALLDIR=%{_datadir}/zsh/site-functions \\\
    FISHINSTALLDIR=%{_datadir}/fish/vendor_completions.d \\\
    BUILDTAGS="grpcnotrace seccomp systemd libsubid libsqlite3" \\\
    GOMD2MAN=%{_bindir}/go-md2man \\\
    GIT_COMMIT= \\\
    SELINUXOPT=

%description
Podman is a daemonless container engine for developing, managing, and
running OCI containers and pods.  It provides a Docker-compatible command
line, rootless containers, pods, quadlet systemd integration and a REST API
service.

This package is built from source and installs podman, podman-remote,
podmansh, quadlet with its systemd generators, rootlessport, the API
service and socket units, auto-update, restart and clean-transient units
for the system and user managers, man pages and shell completions.  The
OCI runtime and helpers come from the crun, conmon, netavark,
aardvark-dns, catatonit and pasta packages.

/etc/containers holds the Tenko defaults: crun, journald logging and
events, the cgroupfs cgroup manager and native rootless overlay storage.

%prep
%setup -q
tar -xzf %{SOURCE1} --strip-components=4 \
    container-libs-common-v0.70.0/common/pkg/seccomp/seccomp.json

%build
export GOPATH="$PWD/.gopath"
export GOFLAGS="-trimpath -modcacherw"
export GOTOOLCHAIN=local
%{podman_make} podman podman-remote rootlessport quadlet docs

%install
rm -rf %{buildroot}
%{podman_make} DESTDIR=%{buildroot} \
    install.bin install.remote install.man install.systemd \
    install.completions

install -d %{buildroot}%{_sysconfdir}/containers
install -m644 %{SOURCE2} %{buildroot}%{_sysconfdir}/containers/containers.conf
install -m644 %{SOURCE3} %{buildroot}%{_sysconfdir}/containers/storage.conf
install -m644 %{SOURCE4} %{buildroot}%{_sysconfdir}/containers/policy.json
install -m644 %{SOURCE5} %{buildroot}%{_sysconfdir}/containers/registries.conf
install -m644 seccomp.json %{buildroot}%{_sysconfdir}/containers/seccomp.json

install -Dm644 README.md %{buildroot}%{_docdir}/podman/README.md
install -Dm644 LICENSE %{buildroot}%{_licensedir}/podman/LICENSE

%files -f %{_sourcedir}/podman.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 6.2.0-1
- New package, not in the base set: latest upstream stable release
  (6.2.0, checked 2026-11-14), built from source.  Replaces the
  podman-bin static bundle (Obsoletes podman-bin < 6.1.4-7).
- Helpers come from the crun, conmon, netavark, aardvark-dns, catatonit and
  pasta packages at podman's default paths; containers.conf sets crun,
  journald logging and events and keeps cgroupfs.
- seccomp.json from containers/common v0.70.0 (the vendored version);
  policy.json and registries.conf as shipped by podman-bin.
