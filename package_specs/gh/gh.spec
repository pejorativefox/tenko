Name:       gh
Version:    2.103.3
Release:    2
Summary:    GitHub's official command line tool
License:    MIT
URL:        https://cli.github.com/
Source0:    gh-%{version}.tar.gz
Prefix:     /usr
ExclusiveArch: x86_64

BuildRequires: go
BuildRequires: make-ca

# Built from source with the go toolchain in /opt/go; the Go modules are
# downloaded during the build and verified against go.sum.
#
# Not in the base set; 2.103.3 is the latest stable upstream release
# (2026-10-26).

%description
gh is GitHub's official command line tool.  It brings pull requests,
issues, releases, repositories, Actions workflows, codespaces and the
GitHub API to the terminal, and supports extensions for additional
commands.

%prep
%setup -q -n cli-%{version}

%build
export GOROOT=/opt/go
export PATH=/opt/go/bin:$PATH
export GOPATH="$PWD/.gopath"
export GOFLAGS=-modcacherw
export GOTOOLCHAIN=local
export CGO_ENABLED=0
export GH_VERSION=%{version}
export SOURCE_DATE_EPOCH=1793042408
export GO_LDFLAGS="-s -w"
go run script/build.go bin/gh manpages
./bin/gh completion -s bash > gh.bash
./bin/gh completion -s zsh > _gh
./bin/gh completion -s fish > gh.fish

%install
rm -rf %{buildroot}
install -Dm755 bin/gh %{buildroot}%{_bindir}/gh
install -d %{buildroot}%{_mandir}/man1
install -m644 share/man/man1/*.1 %{buildroot}%{_mandir}/man1/
install -Dm644 gh.bash %{buildroot}%{_datadir}/bash-completion/completions/gh
install -Dm644 _gh %{buildroot}%{_datadir}/zsh/site-functions/_gh
install -Dm644 gh.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/gh.fish
install -Dm644 README.md %{buildroot}%{_docdir}/gh/README.md
install -Dm644 LICENSE %{buildroot}%{_licensedir}/gh/LICENSE

%files -f %{_sourcedir}/gh.filelist

%changelog
* Fri Nov 13 2026 tenko <build@tenko.invalid> 2.103.3-2
- Download the Go modules at build time (pinned and verified by go.sum)
  instead of from a separately hosted vendor bundle.  Same version.

* Tue Nov 10 2026 browneye <build@browneye.invalid> 2.103.3-1
- New package: GitHub CLI 2.103.3, the latest stable upstream release
  (2026-10-26).  Not in the base set.
- Built from source with the shipped go-bin toolchain; the Go modules are
  vendored as a separate source so rpmbuild can run offline.
- Ship bash, fish and zsh completions and the generated man pages.
