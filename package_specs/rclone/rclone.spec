Name:       rclone
Version:    1.75.2
Release:    2
Summary:    Command-line cloud storage synchronization tool
License:    MIT
URL:        https://rclone.org/
Source0:    rclone-v%{version}.tar.gz
Prefix:     /usr

BuildRequires: go
BuildRequires: make-ca

# Built from source with the distro go toolchain; the Go modules are
# downloaded during the build and verified against go.sum.
#
# Not in the base set; latest upstream stable, needed by the
# publish scripts for the Cloudflare R2 target (issue #20).

%description
rclone is a command-line program to manage files on cloud storage.  It
supports over seventy providers (S3/R2, WebDAV, SFTP, Google Drive, …) and
can copy, sync, check, mount and serve remote storage.

%prep
%setup -q -n rclone-%{version}

%build
export GOPATH="$PWD/.gopath"
export GOFLAGS=-modcacherw
export GOTOOLCHAIN=local
export CGO_ENABLED=0
go build -trimpath -ldflags "-s -w -X github.com/rclone/rclone/fs.Version=v%{version}" -o rclone .
./rclone completion bash > rclone.bash
./rclone completion zsh - > _rclone

%install
rm -rf %{buildroot}
install -Dm755 rclone %{buildroot}%{_bindir}/rclone
install -Dm644 rclone.1 %{buildroot}%{_mandir}/man1/rclone.1
install -Dm644 rclone.bash %{buildroot}%{_datadir}/bash-completion/completions/rclone
install -Dm644 _rclone %{buildroot}%{_datadir}/zsh/site-functions/_rclone
install -Dm644 README.md %{buildroot}%{_docdir}/rclone/README.md
install -Dm644 MANUAL.md %{buildroot}%{_docdir}/rclone/MANUAL.md
install -Dm644 COPYING %{buildroot}%{_licensedir}/rclone/COPYING

%files -f %{_sourcedir}/rclone.filelist

%changelog
* Fri Nov 13 2026 tenko <build@tenko.invalid> 1.75.2-2
- Download the Go modules at build time (pinned and verified by go.sum)
  instead of from a separately hosted vendor bundle.  Same version.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 1.75.2-1
- Not in the base set; latest upstream stable (2026-10-09).
  Needed to publish the repository to Cloudflare R2 (issue #20).
- Built from source with the shipped go-bin toolchain; dependencies are
  vendored as a separate source so rpmbuild can run offline.
