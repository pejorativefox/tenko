Name:       micro
Version:    2.0.15
Release:    1
Summary:    Modern and intuitive terminal-based text editor
License:    MIT AND Apache-2.0 AND BSD-3-Clause AND MPL-2.0
URL:        https://micro-editor.github.io/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
ExclusiveArch: x86_64

BuildRequires: go
BuildRequires: make-ca

# Built from source with the distro go toolchain; the Go modules are
# downloaded during the build and verified against go.sum.
#
# The upstream Makefile reads the version and commit from a git checkout,
# which the release tarball is not, so the build sets them here.
%global commit      6a62575
%global commit_date December 31, 2025

%description
micro is a terminal-based text editor that aims to be easy to use and
intuitive, with common key bindings (Ctrl-S, Ctrl-C, Ctrl-V, Ctrl-Z),
mouse support, syntax highlighting for over 130 languages, multiple
cursors, splits and tabs, and a Lua plugin system.  It is a single static
binary with its runtime files embedded.

%prep
%setup -q

%build
export GOPATH="$PWD/.gopath"
export GOFLAGS=-modcacherw
export GOTOOLCHAIN=local
export CGO_ENABLED=0
go generate ./runtime
go build -trimpath -ldflags "-s -w \
    -X github.com/zyedidia/micro/v2/internal/util.Version=%{version} \
    -X github.com/zyedidia/micro/v2/internal/util.CommitHash=%{commit} \
    -X 'github.com/zyedidia/micro/v2/internal/util.CompileDate=%{commit_date}'" \
    ./cmd/micro

%check
export GOPATH="$PWD/.gopath"
export GOFLAGS=-modcacherw
export GOTOOLCHAIN=local
export CGO_ENABLED=0
go test ./internal/... ./cmd/...
test "$(./micro -version | head -n1)" = "Version: %{version}"

%install
rm -rf %{buildroot}
install -Dm755 micro %{buildroot}%{_bindir}/micro
install -Dm644 assets/packaging/micro.1 %{buildroot}%{_mandir}/man1/micro.1
install -Dm644 assets/packaging/micro.desktop \
    %{buildroot}%{_datadir}/applications/micro.desktop
install -Dm644 assets/micro-logo-mark.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/micro.svg
install -Dm644 data/io.github.zyedidia.micro.metainfo.xml \
    %{buildroot}%{_datadir}/metainfo/io.github.zyedidia.micro.metainfo.xml
install -Dm644 README.md %{buildroot}%{_docdir}/micro/README.md
install -Dm644 LICENSE %{buildroot}%{_licensedir}/micro/LICENSE
install -Dm644 LICENSE-THIRD-PARTY \
    %{buildroot}%{_licensedir}/micro/LICENSE-THIRD-PARTY

%files -f %{_sourcedir}/micro.filelist

%changelog
* Mon Nov 16 2026 tenko <build@tenko.invalid> 2.0.15-1
- New package, not in the base set: latest upstream stable release
  (2.0.15, checked 2026-11-16).  Built from source with the upstream
  version, commit and release date stamped in; ships the man page,
  desktop entry, icon and AppStream metadata.
