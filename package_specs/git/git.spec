# git installs its git-core commands as hardlinks to a single binary; stripping
# the same inode repeatedly fails in %%__spec_install_post.
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}
# Optional git subcommands (git svn, git send-email, git gui) need Perl modules
# that are not in the base system; do not make the core package depend on them.
%global __requires_exclude ^perl\\(

Name:       git
Version:    2.56.0
Release:    2
Summary:    Distributed version control system
License:    GPL-2.0-only
URL:        https://git-scm.com/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: curl
BuildRequires: expat
BuildRequires: openssl
BuildRequires: pcre2
BuildRequires: perl
BuildRequires: zlib
Requires:      perl

%description
Git is a free and open source distributed version control system designed
to handle everything from small to very large projects with speed and
efficiency.

%package lang
Summary:    git translations
Requires:   git = %{version}-%{release}

%description lang
Translations for git.

%prep
%setup -q

%build
%configure --prefix=/usr                   \
           --with-gitconfig=/etc/gitconfig \
           --with-python=python3           \
           --with-libpcre2
make -j8 NO_RUST=1

%install
rm -rf %{buildroot}
make perllibdir=/usr/lib/perl5/5.44.0/site_perl install DESTDIR=%{buildroot} NO_RUST=1
mkdir -p %{buildroot}/etc/bash_completion.d
cp contrib/completion/git-completion.bash %{buildroot}/etc/bash_completion.d/
# The rest of git's contrib/completion tree is not installed by make install.
# Install it under the Fedora-compatible path so existing prompts find
# git-prompt.sh without further configuration (issue #25).
install -d %{buildroot}/usr/share/git-core/contrib/completion
install -m644 contrib/completion/git-prompt.sh \
    %{buildroot}/usr/share/git-core/contrib/completion/
install -m644 contrib/completion/git-completion.tcsh \
    %{buildroot}/usr/share/git-core/contrib/completion/
install -m644 contrib/completion/git-completion.zsh \
    %{buildroot}/usr/share/git-core/contrib/completion/

%files -f %{_sourcedir}/git.filelist
%files lang -f %{_sourcedir}/git-lang.filelist


%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 2.56.0-2
- Package git-prompt.sh and the tcsh/zsh completions from
  contrib/completion under /usr/share/git-core/contrib/completion.
  Only git-completion.bash was installed before, so prompts using
  __git_ps1 fell back to the branch-only implementation (issue #25).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 2.56.0-1
- Update to 2.56.0 (current upstream version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.55.0-2
- Split lang payload into git-lang (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.55.0
- Update to 2.55.0
- Use the documented configure options and skip the Rust components
- Install Perl modules under /usr/lib/perl5/5.44.0/site_perl
- Replace the directory listing with a generated static filelist
