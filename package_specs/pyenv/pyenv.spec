# pyenv is a set of bash scripts; nothing is compiled.  The installation
# prefix is /usr/share/pyenv and /usr/bin/pyenv is a symlink into it.  pyenv
# resolves its own prefix through that symlink, while PYENV_ROOT (where the
# interpreter versions and shims live) stays a per-user directory and
# defaults to ~/.pyenv.
%global debug_package %{nil}

Name:       pyenv
Version:    2.8.14
Release:    1
Summary:    Simple Python version management
License:    MIT
URL:        https://github.com/pyenv/pyenv
Source0:    pyenv-2.8.14.tar.gz
Source1:    pyenv.sh
BuildArch:  noarch
Prefix:     /usr

Requires:   bash
Requires:   coreutils
Requires:   findutils
Requires:   gawk
Requires:   grep
Requires:   sed
Requires:   tar
Requires:   gzip
Requires:   bzip2
Requires:   xz
Requires:   curl
Requires:   git

%description
pyenv lets you easily switch between multiple versions of Python.  It is a
set of shell scripts that shim the python, pip and other interpreter
commands, so a per-directory or per-shell version can be selected without
touching the system Python.

This package installs the complete pyenv 2.8.14 tree (including the
bundled python-build, pyenv-binary and pyenv-link plugins) under
/usr/share/pyenv and links /usr/bin/pyenv to it.  PYENV_ROOT defaults to
~/.pyenv, which is where pyenv installs interpreters and creates its shims;
/usr/share/pyenv stays read-only.

/etc/profile.d/pyenv.sh initialises pyenv for bash login shells once the
user has a PYENV_ROOT (pyenv install creates ~/.pyenv), so the shims and
completions become active automatically.  Users of other shells can add the
matching upstream line to their own startup file, for example
"eval \"$(pyenv init - zsh)\"".  To install an interpreter, run
"pyenv install --list" and "pyenv install <version>"; compiling CPython
additionally needs the usual Python build environment (gcc, make and the
-devel libraries), which pyenv reports as missing when a build fails.

pyenv is not part of the base set.  The user approved upstream 2.8.14
as an explicit exception to the Tenko version-policy rule.

%prep
%setup -q

%build

%install
rm -rf %{buildroot}
install -d -m755 %{buildroot}%{_datadir}/pyenv
cp -a bin libexec plugins pyenv.d src completions \
    %{buildroot}%{_datadir}/pyenv/
install -d -m755 %{buildroot}%{_bindir}
ln -s %{_datadir}/pyenv/bin/pyenv %{buildroot}%{_bindir}/pyenv
install -D -m644 man/man1/pyenv.1 %{buildroot}%{_mandir}/man1/pyenv.1
install -D -m644 %{SOURCE1} %{buildroot}%{_sysconfdir}/profile.d/pyenv.sh
install -d -m755 %{buildroot}%{_datadir}/doc/pyenv-%{version}
install -m644 LICENSE README.md COMMANDS.md CHANGELOG.md \
    %{buildroot}%{_datadir}/doc/pyenv-%{version}/

%files -f %{_sourcedir}/pyenv.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 2.8.14-1
- New package: pyenv 2.8.14 from the upstream release tarball.  pyenv is
  not in the base set; the user approved it as a version-policy exception.
- Install the full tree under /usr/share/pyenv and link /usr/bin/pyenv, so
  PYENV_ROOT (~/.pyenv) remains a per-user, writable directory.
- /etc/profile.d/pyenv.sh initialises bash login shells once ~/.pyenv
  exists; completions are sourced from the install prefix by pyenv init.
- Source: https://github.com/pyenv/pyenv/archive/refs/tags/v2.8.14.tar.gz
  md5 78522466e9626537123f3fc05910b718
  sha256 0db903040bd06f4adc333bff60aefbdfc4af522f8e2b13f9cce3fbf721b3e468
- Requires the shell utilities pyenv and python-build call at runtime, plus
  curl (definitions download tarballs) and git (development/install_git
  definitions); the compiler and -devel headers needed to build CPython are
  left to the user, as upstream documents.
