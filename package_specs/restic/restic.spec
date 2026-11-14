Name:       restic
Version:    0.19.1
Release:    2
Summary:    Fast, secure and efficient backup program
License:    BSD-2-Clause
URL:        https://restic.net/
Source0:    restic-%{version}.tar.gz
Prefix:     /usr
ExclusiveArch: x86_64

BuildRequires: go
BuildRequires: make-ca

# Built from source with the distro go toolchain; the Go modules are
# downloaded during the build and verified against go.sum.
# The selfupdate build tag is deliberately omitted: updates are delivered by
# the distro repository instead of restic's own GitHub downloader.
#
# Not in the base set; 0.19.1 is the latest stable upstream release
# (2026-07-05).

%description
restic is a backup program that is fast, efficient and secure.  It supports
local and remote repositories (SFTP, REST, S3, Backblaze B2, Microsoft Azure,
Google Cloud Storage and others), deduplicates data, encrypts it with AES-256
and provides snapshot-based restore, retention policies and repository checks.

%prep
%setup -q

%build
export GOPATH="$PWD/.gopath"
export GOFLAGS=-modcacherw
export GOTOOLCHAIN=local
export CGO_ENABLED=0
go build -trimpath -tags "disable_grpc_modules" -ldflags "-s -w" \
    -o restic ./cmd/restic
mkdir -p man
./restic generate \
    --man man \
    --bash-completion restic.bash \
    --zsh-completion _restic \
    --fish-completion restic.fish

%install
rm -rf %{buildroot}
install -Dm755 restic %{buildroot}%{_bindir}/restic
install -d %{buildroot}%{_mandir}/man1
install -m644 man/*.1 %{buildroot}%{_mandir}/man1/
install -Dm644 restic.bash \
    %{buildroot}%{_datadir}/bash-completion/completions/restic
install -Dm644 _restic %{buildroot}%{_datadir}/zsh/site-functions/_restic
install -Dm644 restic.fish \
    %{buildroot}%{_datadir}/fish/vendor_completions.d/restic.fish
install -Dm644 README.md %{buildroot}%{_docdir}/restic/README.md
install -Dm644 CHANGELOG.md %{buildroot}%{_docdir}/restic/CHANGELOG.md
install -Dm644 LICENSE %{buildroot}%{_licensedir}/restic/LICENSE

%files -f %{_sourcedir}/restic.filelist

%changelog
* Fri Nov 13 2026 tenko <build@tenko.invalid> 0.19.1-2
- Download the Go modules at build time (pinned and verified by go.sum)
  instead of from a separately hosted vendor bundle.  Same version.

* Tue Nov 10 2026 browneye <build@browneye.invalid> 0.19.1-1
- New package: restic 0.19.1, the latest stable upstream release
  (2026-07-05).  Not in the base set.
- Built from source with the shipped go-bin toolchain; the Go modules are
  vendored as a separate source so rpmbuild can run offline.  The
  selfupdate tag is omitted so updates come from the distro repository.
- Ship bash, fish and zsh completions and the generated man pages.
