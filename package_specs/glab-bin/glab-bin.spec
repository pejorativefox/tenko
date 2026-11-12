# glab ships as a self-contained, statically linked Go binary.  Leave the
# upstream payload exactly as published: it is already stripped, and rpm's
# strip/debug helpers would only touch it.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       glab-bin
Version:    1.130.0
Release:    1
Summary:    Official GitLab command-line tool (prebuilt linux-amd64 binary)
License:    MIT
URL:        https://gitlab.com/gitlab-org/cli
Source0:    glab_%{version}_linux_amd64.tar.gz

ExclusiveArch: x86_64

# Prebuilt static binary: rpm must not guess dependencies from it.
AutoProv: no
AutoReq: no

Provides: glab = %{version}-%{release}

# git is used to discover remotes and to clone repositories; make-ca owns
# the CA trust store glab uses for HTTPS.
Requires: git
Requires: make-ca

BuildRequires: gzip
BuildRequires: tar

%description
GLab is GitLab's official command-line tool.  It works next to git in the
terminal: issues, merge requests, CI/CD pipelines, releases, repository
operations, the GitLab API and more.

This package installs the official prebuilt linux-amd64 release binary, a
statically linked Go executable with no runtime language dependencies, plus
its bash, fish and zsh completions.  glab is not part of the base set; the
user approved packaging the official prebuilt binary.

%prep
%setup -q -c -n %{name}-%{version}

%build
# Generate the shell completions from the shipped binary.
HOME=$PWD ./bin/glab completion -s bash > glab.bash
HOME=$PWD ./bin/glab completion -s zsh > _glab
HOME=$PWD ./bin/glab completion -s fish > glab.fish

%install
rm -rf %{buildroot}
install -Dm755 bin/glab %{buildroot}%{_bindir}/glab
install -Dm644 glab.bash %{buildroot}%{_datadir}/bash-completion/completions/glab
install -Dm644 _glab %{buildroot}%{_datadir}/zsh/site-functions/_glab
install -Dm644 glab.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/glab.fish
install -Dm644 README.md %{buildroot}%{_docdir}/glab-bin/README.md
install -Dm644 CHANGELOG.md %{buildroot}%{_docdir}/glab-bin/CHANGELOG.md
install -Dm644 LICENSE %{buildroot}%{_licensedir}/glab-bin/LICENSE

%files -f %{_sourcedir}/glab-bin.filelist

%changelog
* Thu Nov 12 2026 tenko <build@tenko.invalid> 1.130.0-1
- New package, not in the base set: official prebuilt linux-amd64 release
  of glab 1.130.0, the latest stable upstream release (2026-11-10).
  User-approved bin package.
