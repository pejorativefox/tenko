Name:       go
Version:    1.27.3
Release:    2
Summary:    The go programming language (golang)
License:    BSD-3-Clause
URL:        https://go.dev/
Source0:    go%{version}.src.tar.gz
Prefix:     /usr
ExclusiveArch: x86_64

# Replaces the repackaged upstream binary (go-bin).  Packages that still
# ask for go-bin get this one.
Provides:   go-bin = %{version}-%{release}
Obsoletes:  go-bin < 1.27.3-3

# Go is written in Go: make.bash needs an installed toolchain of at least
# the version in src/cmd/dist/buildtool.go (minBootstrap, go1.24.6 for
# 1.27).  The installed go is that bootstrap, so each release is built by
# the previous one.
BuildRequires: go
BuildRequires: bash

# md5 of upstream's linux-amd64 binary tarball.  make.bash -distpack
# reproduces upstream's release tarball byte for byte; the check section
# fails if this build does not, so the shipped toolchain is proven to match the source.
%global upstream_md5 747a0477c6bacb93924ac08721a61a81

# The tree ships cross-architecture test objects that strip cannot read.
# Leave the toolchain payload exactly as distpack writes it.
%global __strip /bin/true

# The toolchain is self-contained; some testdata fixtures are shared
# libraries that would otherwise add bogus runtime requires (libtiff).
AutoReqProv: no

# Installed as the distro toolchain at /usr/lib64/go (GOROOT) with go and
# gofmt linked into /usr/bin.  The go command derives GOROOT from its own
# path, so no environment setup is needed.

%description
Go is a statically typed, compiled high-level programming language.

%prep
%setup -q -n go

%build
cd src
unset GOROOT
export GOROOT_BOOTSTRAP=$(GOENV=off /usr/bin/go env GOROOT)
export GOTOOLCHAIN=local
export GOPROXY=off
export GOCACHE=%{_builddir}/go-cache
export GOENV=off
unset GOPATH GOFLAGS CGO_ENABLED
./make.bash -distpack

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_libdir}
tar -xzf pkg/distpack/go%{version}.linux-amd64.tar.gz -C %{buildroot}%{_libdir}
for f in run make clean all; do rm %{buildroot}%{_libdir}/go/src/$f.rc; done

install -d %{buildroot}%{_bindir}
ln -s ../lib64/go/bin/go %{buildroot}%{_bindir}/go
ln -s ../lib64/go/bin/gofmt %{buildroot}%{_bindir}/gofmt

%check
echo "%{upstream_md5}  pkg/distpack/go%{version}.linux-amd64.tar.gz" | md5sum -c -

%files -f %{_sourcedir}/go.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 1.27.3-2
- Install the source-built toolchain at /usr/lib64/go instead of /opt/go
  (/opt is for repackaged binary bundles).  go and gofmt link into
  /usr/bin; drop /etc/profile.d/go_path.sh, since go finds its GOROOT from
  its own path.  Shells started before the upgrade keep GOROOT=/opt/go
  until the next login.  Same version (1.27.3).

* Fri Nov 13 2026 tenko <build@tenko.invalid> 1.27.3-1
- Build the toolchain from the upstream source release instead of
  repackaging the binary tarball (go-bin, which this replaces).  1.27.3 is
  the latest upstream stable (checked 2026-11-13).  make.bash -distpack
  reproduces upstream's linux-amd64 tarball byte for byte, which the check
  section verifies.  Bootstrapped from the installed toolchain.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 1.27.3-2
- Link go and gofmt into /usr/bin like the other /opt bundles, so desktop
  launchers, systemd units, cron and non-login shells find the toolchain
  without reading /etc/profile.d.  The profile.d snippet keeps GOROOT and
  a convenience PATH entry, now idempotent.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.27.3-1
- Not in the base set; 1.27.3 is the latest upstream stable
  (2026-11-05).
- Install the complete Go tree (VERSION, go.env, test, ...) instead of
  the old subset, and refresh the file list from the payload.

* Sun Jun 18 2023 Chris Statzer <chris.statzer@gmail.com> 1.20.5
- Version bump

* Tue May 12 2020 Chris Statzer <chris.statzer@qq.com> 1.12.7
- Initial RPM
- Added path to default bash profile
