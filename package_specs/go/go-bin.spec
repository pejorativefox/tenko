Name:       go-bin
Version:    1.27.3
Release:    2
Summary:    The go programming language (golang)
License:    BSD-3-Clause
Source0:    go%{version}.linux-amd64.tar.gz
Prefix:     /usr

# The bundle ships cross-architecture test objects that strip cannot read.
# Leave the toolchain payload exactly as upstream publishes it.
%global __strip /bin/true

# The toolchain is self-contained; some testdata fixtures are shared
# libraries that would otherwise add bogus runtime requires (libtiff).
AutoReqProv: no

%description
Go is a statically typed, compiled high-level programming language.

%prep
%setup -n go

%build 

%install    
rm -rf %{buildroot}
mkdir -pv %{buildroot}/opt/go
cp -a . %{buildroot}/opt/go

mkdir -pv %{buildroot}/etc/profile.d
cat > %{buildroot}/etc/profile.d/go_path.sh << "EOF"
# GOROOT points tools at the bundle; the go and gofmt entry points are in
# /usr/bin, so PATH is only a convenience for shells that already read
# /etc/profile.d.  Keep the PATH update idempotent.
export GOROOT=/opt/go
case ":$PATH:" in
    *:/opt/go/bin:*) ;;
    *) PATH="$PATH:/opt/go/bin" ;;
esac
export PATH
EOF

# Every user-facing command is linked into /usr/bin, like the other /opt
# bundles: desktop launchers, systemd units and non-login shells do not read
# /etc/profile.d.
install -d %{buildroot}%{_bindir}
ln -s /opt/go/bin/go %{buildroot}%{_bindir}/go
ln -s /opt/go/bin/gofmt %{buildroot}%{_bindir}/gofmt
rm %{buildroot}/opt/go/src/run.rc
rm %{buildroot}/opt/go/src/make.rc
rm %{buildroot}/opt/go/src/clean.rc
rm %{buildroot}/opt/go/src/all.rc

%files -f %{_sourcedir}/go-bin.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 1.27.3-2
- Link go and gofmt into /usr/bin like the other /opt bundles, so desktop
  launchers, systemd units, cron and non-login shells find the toolchain
  without reading /etc/profile.d.  The profile.d snippet keeps GOROOT and
  a convenience PATH entry, now idempotent.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.27.3-1
- Not in the base set; 1.27.3 is the latest upstream stable
  (2026-11-05).
- Install the complete Go tree (VERSION, go.env, test, ...) instead of
  the old subset, and refresh %files from the payload.

* Sun Jun 18 2023 Chris Statzer <chris.statzer@gmail.com> 1.20.5
- Version bump

* Tue May 12 2020 Chris Statzer <chris.statzer@qq.com> 1.12.7
- Initial RPM
- Added path to default bash profile
