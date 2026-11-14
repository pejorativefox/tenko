Name:       crun
Version:    1.31
Release:    1
Summary:    Lightweight OCI container runtime written in C
License:    GPL-2.0-or-later
URL:        https://github.com/containers/crun
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: json-c
BuildRequires: libcap
BuildRequires: libseccomp
BuildRequires: systemd

%description
crun is a fast, low-memory OCI runtime written in C.  podman uses it to
create and run containers.  This build supports systemd cgroups, seccomp
filters and capabilities; the release tarball bundles libocispec.

%prep
%setup -q

%build
%configure \
    --disable-libcrun \
    --disable-static \
    --enable-embedded-blake3 \
    --disable-criu
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/crun.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 1.31-1
- New package, not in the base set: latest upstream stable release
  (1.31, checked 2026-11-14).  OCI runtime for podman, replacing the
  crun in the podman-bin bundle; built with systemd, seccomp and libcap.
