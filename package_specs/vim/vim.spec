Name:       vim
Version:    9.2.1225
Release:    3
Summary:    vi Improved Text editor
License:    Vim
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

Requires:   vim-minimal = %{version}-%{release}
Requires:   vim-runtime-extra = %{version}-%{release}

%description
Vim is a highly configurable text editor built to make creating and changing any kind of text very efficient. It is included as "vi" with most UNIX systems and with Apple OS X.

This is a meta package: it installs vim-minimal (the editor) and
vim-runtime-extra (the full runtime) and contains no files of its own.

%prep
%setup -q

%build
echo '#define SYS_VIMRC_FILE "/etc/vimrc"' >> src/feature.h
%configure --enable-gui=no --without-x --disable-selinux --disable-canberra --disable-pixman --without-wayland
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
rm %{buildroot}/usr/share/applications/gvim.desktop
rm -rf %{buildroot}/usr/share/icons/*
rm -rf %{buildroot}/usr/share/vim/vim92/tools/vim132
rm -f %{buildroot}/usr/share/vim/vim92/tools/demoserver.py

%package minimal
Summary:    Minimal Vim editor and runtime

%description minimal
The Vim editor binary and the runtime needed to edit files: syntax
highlighting, filetype plugins, indentation, colour schemes, compiler and
keymap definitions, the basic help files, and the netrw file browser.
netrw stays here even though it is a bundled package: the core
plugin/netrwPlugin.vim is loaded on every start and runs `packadd netrw`,
so splitting them makes vim fail with E919.  The remaining documentation,
spelling, tutor, translations, bundled packages and localised man pages are
in vim-runtime-extra.

%package runtime-extra
Summary:    Extra Vim runtime (documentation, spelling, tutor, translations)
Requires:   vim-minimal = %{version}-%{release}

%description runtime-extra
The optional Vim runtime data: the full reference and user documentation,
spell files, the vimtutor lessons, translations, the bundled packages other
than netrw, and the localised man pages.

%files
%files minimal -f %{_sourcedir}/vim-minimal.filelist
%files runtime-extra -f %{_sourcedir}/vim-runtime-extra.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 9.2.1225-3
- Record the verified license (Vim): LICENSE (issue #8).

* Tue Nov  3 2026 browneye <build@browneye.invalid> 9.2.1225-2
- Move the netrw package (pack/dist/opt/netrw) from vim-runtime-extra to
  vim-minimal: plugin/netrwPlugin.vim ships in vim-minimal and runs
  `packadd netrw` at startup, so a base install without vim-runtime-extra
  aborted with E919 "Directory not found in 'packpath'"
- Configure --disable-pixman: with no GUI/X11 there is no use for pixman,
  and the auto-detection made the editor depend on whatever the build
  image happened to have installed

* Mon Nov  2 2026 browneye <build@browneye.invalid> 9.2.1225-1
- Update to 9.2.1225 (current LFS/BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 9.2.1099-3
- Bump the release for the vim-minimal/vim-runtime-extra split: the
  9.2.1099-2 build is already published with the old monolithic payload,
  so the split needs a new NEVR for upgrades to install it

* Sun Nov 01 2026 browneye <build@browneye.invalid> 9.2.1099-2
- Split vim-minimal (binary plus the editing runtime) and
  vim-runtime-extra (full docs, spell, tutor, translations, packages and
  man pages); vim remains the meta package that requires both
- Disable libcanberra so the base editor does not pull GTK3 (size audit P0)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 9.2.1025
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 9.0.1677-1
- Version bump

* Fri May 15 2020 Chris Statzer <chris.statzer@qq.com> 8.1-4
- Removed gtk/X11 build

