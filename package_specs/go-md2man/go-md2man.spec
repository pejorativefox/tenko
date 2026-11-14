Name:       go-md2man
Version:    2.0.7
Release:    1
Summary:    Convert Markdown to roff man pages
License:    MIT
URL:        https://github.com/cpuguy83/go-md2man
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
ExclusiveArch: x86_64

BuildRequires: go
BuildRequires: make-ca

# Built from source with the distro go toolchain; the Go modules are
# downloaded during the build and verified against go.sum.

%description
go-md2man converts Markdown documents into roff man pages.  Go projects
such as podman use it to generate their manual pages at build time.

%prep
%setup -q

%build
export GOPATH="$PWD/.gopath"
export GOFLAGS=-modcacherw
export GOTOOLCHAIN=local
export CGO_ENABLED=0
go build -trimpath -ldflags "-s -w" -o bin/go-md2man .
./bin/go-md2man -in go-md2man.1.md -out go-md2man.1

%install
rm -rf %{buildroot}
install -Dm755 bin/go-md2man %{buildroot}%{_bindir}/go-md2man
install -Dm644 go-md2man.1 %{buildroot}%{_mandir}/man1/go-md2man.1
install -Dm644 README.md %{buildroot}%{_docdir}/go-md2man/README.md
install -Dm644 LICENSE.md %{buildroot}%{_licensedir}/go-md2man/LICENSE.md

%files -f %{_sourcedir}/go-md2man.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 2.0.7-1
- New package, not in the base set: latest upstream stable release
  (2.0.7, checked 2026-11-14).  Built from source; podman needs it to
  generate its man pages.
