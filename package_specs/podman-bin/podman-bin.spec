# Static upstream full-podman bundle (mgoltzsche/podman-static) installed
# under /opt.  This is a binary repackage, not a source build.
#
# The bundle is fully static (musl, no glibc) and contains podman 6.1.4 with
# its helpers: crun 1.30.1, runc 1.5.2, conmon 2.2.1, netavark/aardvark-dns
# 2.1.0, pasta/passt 2026_10_02.cba3570, fuse-overlayfs 1.18 (libfuse
# 3.18.3) and catatonit 0.2.1.
#
# podman and every one of its components are absent from LFS/BLFS r13.1, so
# the version-parity rule in AGENTS.md cannot be satisfied from the books.
# The user explicitly approved this third-party static bundle as an
# exception (recon: options A vs B vs D).
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       podman-bin
Version:    6.1.4
Release:    2
Summary:    Podman container engine and helpers (static upstream bundle)
License:    Apache-2.0 AND GPL-2.0-or-later
URL:        https://github.com/mgoltzsche/podman-static
# v6.1.4 asset podman-linux-amd64.tar.gz, 34864320 bytes
#   sha256 9dd51073fac5a1742f88cf3caff5554615cb4d67ba554d25e8807be635547af5
#   md5    9f5803ca7fa377e06024e30bd195bc97  (also in ./sources)
#   GPG    Max Goltzsche, 0CCF102C4F95D89E583FF1D4F8B5AF50344BB503
Source0:    podman-linux-amd64-%{version}.tar.gz
Source1:    containers.conf
Source2:    storage.conf

ExclusiveArch: x86_64

# Prebuilt static payload: rpm must not guess dependencies from binaries
# under /opt.  The explicit runtime list below is the real host requirement.
AutoProv: no
AutoReq: no

Provides:   podman = %{version}-%{release}

# newuidmap/newgidmap (setuid) for rootless multi-ID mapping
Requires:   shadow
# nsenter, unshare
Requires:   util-linux
# overlays, fuse, netfilter module autoload
Requires:   kmod
# /run/user/$UID and cgroup delegation for the rootless session
Requires:   systemd
# /etc/subuid and /etc/subgid, which this package no longer ships
Requires:   browneye-sysconfig

%description
Podman is a daemonless container engine for developing, managing, and
running OCI containers and pods.

This package repackages the static podman 6.1.4 bundle published by
mgoltzsche/podman-static under /opt/podman-6.1.4 (with /opt/podman as a
stable symlink and /usr/bin/podman as the PATH entry point).  It includes
the bundled crun, runc, conmon, netavark, aardvark-dns, pasta/passt,
fuse-overlayfs, fusermount3 and catatonit.

The bundled conmon is built without journald support, so
/etc/containers/containers.conf sets log_driver = "k8s-file".  Storage uses
native rootless overlay with no mount_program.  systemd units, generators
and quadlet are not shipped (the bundle compiles /usr/local/bin/podman into
them); use podman from the command line or from the build scripts.

Neither podman nor its dependency chain is part of LFS/BLFS.  The user
explicitly approved packaging this static upstream bundle as an exception
to the Browneye version-parity rule.

%prep
%setup -q -n podman-linux-amd64

%build
# Prebuilt payload: nothing to compile.

%install
rm -rf %{buildroot}

# Payload: the bundle lays everything out under usr/local.  Keep only the
# runtime pieces in the versioned /opt tree; the systemd units/generators
# and quadlet would need /usr/local/bin/podman patched in, so they are not
# installed (see the changelog).
install -d %{buildroot}/opt/podman-%{version}/{bin,libexec,share}
cp -a usr/local/bin/. %{buildroot}/opt/podman-%{version}/bin/
cp -a usr/local/lib/podman/. %{buildroot}/opt/podman-%{version}/libexec/
cp -a usr/local/share/. %{buildroot}/opt/podman-%{version}/share/
ln -s podman-%{version} %{buildroot}/opt/podman

install -d %{buildroot}%{_bindir}
ln -s /opt/podman/bin/podman %{buildroot}%{_bindir}/podman

# Runtime configuration.  containers.conf and storage.conf are Browneye
# specific (bundle conmon has no journald; native overlay without
# mount_program).  policy.json, registries.conf and seccomp.json are taken
# from the bundle unchanged; none of them hardcodes /usr/local.
install -d %{buildroot}/etc/containers
install -m644 %{SOURCE1} %{buildroot}/etc/containers/containers.conf
install -m644 %{SOURCE2} %{buildroot}/etc/containers/storage.conf
install -m644 etc/containers/policy.json \
    %{buildroot}/etc/containers/policy.json
install -m644 etc/containers/registries.conf \
    %{buildroot}/etc/containers/registries.conf
install -m644 etc/containers/seccomp.json \
    %{buildroot}/etc/containers/seccomp.json

# /etc/subuid and /etc/subgid are owned by browneye-sysconfig: shipping them
# here as well made the two packages collide on those paths and blocked the
# install.  login.defs already points at them, and the installer fills in the
# admin user's subordinate range.  Required: browneye-sysconfig (see above).

install -d %{buildroot}%{_docdir}/%{name}-%{version}
install -m644 README.md %{buildroot}%{_docdir}/%{name}-%{version}/README.md

%files -f %{_sourcedir}/podman-bin.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 6.1.4-2
- Stop shipping /etc/subuid and /etc/subgid: browneye-sysconfig already owns
  those paths, so installing podman-bin failed with a transaction file
  conflict.  Require browneye-sysconfig instead and leave the files to it.
  The subordinate range itself is unchanged (subuid/subgid come from
  browneye-sysconfig and the installer's usermod).
* Mon Nov 02 2026 browneye <build@browneye.invalid> 6.1.4-1
- New package: the static podman 6.1.4 bundle from mgoltzsche/podman-static
  under /opt/podman-6.1.4, /opt/podman and /usr/bin/podman symlinks.
  podman, conmon, crun, runc and the rest of the chain are not in LFS/BLFS;
  this is the user-approved option A exception to the version-parity rule.
- Supersedes the stale package_specs/podman 4.5.1 spec, whose install
  layout no longer matches the 6.x tarball.  The old directory is left
  untouched for the integration session to retire.
- Ship /etc/containers/{containers,storage}.conf, policy.json,
  registries.conf and seccomp.json.  log_driver = "k8s-file" because the
  bundled conmon has no journald; overlay storage with NO mount_program
  (native unprivileged overlay on kernel 7.2.6).  The bundle's
  storage.conf.d drop-in and all /usr/local paths are dropped.
- Ship /etc/subuid and /etc/subgid (0644, comment header only) so shadow's
  useradd assigns subordinate ranges; the installer adds the admin user's.
- systemd units, generators and quadlet are deliberately not shipped: they
  hardcode /usr/local/bin/podman (quadlet also compiles it in), and the
  build pipeline does not use them.
