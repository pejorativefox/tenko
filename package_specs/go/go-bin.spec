Name:       go-bin
Version:    1.27.3
Release:    1
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
export PATH=$PATH:/opt/go/bin
export GOROOT=/opt/go
EOF
rm %{buildroot}/opt/go/src/run.rc
rm %{buildroot}/opt/go/src/make.rc
rm %{buildroot}/opt/go/src/clean.rc
rm %{buildroot}/opt/go/src/all.rc

%files
/opt/go/*
/etc/profile.d/go_path.sh

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.27.3-1
- Not in the r13.1 book; 1.27.3 is the latest upstream stable
  (2026-11-05).
- Install the complete Go tree (VERSION, go.env, test, ...) instead of
  the old subset, and refresh %files from the payload.

* Sun Jun 18 2023 Chris Statzer <chris.statzer@gmail.com> 1.20.5
- Version bump

* Tue May 12 2020 Chris Statzer <chris.statzer@qq.com> 1.12.7
- Initial RPM
- Added path to default bash profile
