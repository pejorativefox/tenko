# Kitty ships an official self-contained Linux x86_64 bundle: bin/kitty,
# bin/kitten (static Go), bin/slangc, lib/ (Python 3.14 runtime, GL/UI
# libraries, shaders, shell integration) and share/ (docs, man pages,
# terminfo, desktop files).  This is a binary repackage, not a source build.
#
# Kitty is not part of LFS/BLFS r13.1.  The user explicitly approved
# packaging the official prebuilt bundle as an exception to the version
# parity rule in AGENTS.md.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

# ~160 MiB installed; xz level 6 keeps the RPM near the 45 MiB upstream
# tarball without a large packaging cost.
%global _binary_payload w6.xzdio

Name:       kitty-bin
Version:    0.49.2
Release:    1
Summary:    GPU-based terminal emulator (official prebuilt x86_64 bundle)
License:    GPL-3.0-or-later
URL:        https://sw.kovidgoyal.net/kitty/

# v0.49.2 asset kitty-0.49.2-x86_64.txz, 45897008 bytes
#   sha256 d573618b911e9c461bd421b96c13c74c7f1cb2f1ac9c327818d4ff84366cf5c6
#   md5    85b5b9fb1b655eee879256bc7d19d7b1  (also in ./sources)
Source0:    kitty-%{version}-x86_64.txz
# The bundle has no license file; this is the GPL-3.0 text from the
# matching kitty source release.
Source1:    LICENSE

ExclusiveArch: x86_64

# Prebuilt payload: never let rpm guess provides/requires from the bundled
# libraries under /opt.  The explicit runtime list below is the real host
# requirement; everything else (Python 3.14, harfbuzz, freetype, libpng,
# lcms2, xxhash, OpenSSL, xkbcommon) is bundled in lib/.
AutoProv: no
AutoReq: no

Provides:   kitty = %{version}-%{release}

Requires:   glibc
Requires:   libx11
Requires:   libxcursor
Requires:   dbus-libs
Requires:   mesa
Requires:   fontconfig
Requires:   hicolor-icon-theme

%description
kitty is a fast, feature-rich, GPU-based terminal emulator, split into
tabs and windows, with support for Unicode, true color, ligatures, images,
hyperlinks and shell integration.

This package repackages the official upstream x86_64 release bundle under
/opt/kitty-%{version} (with /opt/kitty as a stable symlink and
/usr/bin/kitty and /usr/bin/kitten as the PATH entry points).  The bundle
is self-contained: it ships its own Python 3.14 runtime, the graphics and
font libraries it needs, the generated shaders, shell integration and a
static Go kitten binary.

kitty is not part of LFS/BLFS.  The user explicitly approved packaging the
official prebuilt bundle as an exception to the Browneye version-parity
rule.

%prep
%setup -q -c -n %{name}-%{version}

%build

%install
rm -rf %{buildroot}

install -d %{buildroot}/opt/kitty-%{version}
cp -a bin lib %{buildroot}/opt/kitty-%{version}/
ln -s kitty-%{version} %{buildroot}/opt/kitty

install -d %{buildroot}%{_bindir}
ln -s /opt/kitty/bin/kitty %{buildroot}%{_bindir}/kitty
ln -s /opt/kitty/bin/kitten %{buildroot}%{_bindir}/kitten

install -d %{buildroot}%{_datadir}/applications
install -m644 share/applications/kitty.desktop \
    share/applications/kitty-open.desktop \
    %{buildroot}%{_datadir}/applications/

install -d %{buildroot}%{_datadir}/icons/hicolor/scalable/apps \
           %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
install -m644 share/icons/hicolor/scalable/apps/kitty.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/
install -m644 share/icons/hicolor/256x256/apps/kitty.png \
    %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/

install -d %{buildroot}%{_mandir}/man1 %{buildroot}%{_mandir}/man5
install -m644 share/man/man1/*.1 %{buildroot}%{_mandir}/man1/
install -m644 share/man/man5/*.5 %{buildroot}%{_mandir}/man5/

# The xterm-kitty terminfo entry is needed on every host that runs the
# shell over ssh (kitty's TERM is xterm-kitty), not just on the desktop.
install -d %{buildroot}%{_datadir}/terminfo/x
install -m644 share/terminfo/x/xterm-kitty \
    %{buildroot}%{_datadir}/terminfo/x/xterm-kitty

install -d %{buildroot}%{_docdir}/kitty
cp -a share/doc/kitty/html %{buildroot}%{_docdir}/kitty/html
install -m644 %{SOURCE1} %{buildroot}%{_docdir}/kitty/LICENSE

%files -f %{_sourcedir}/kitty-bin.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.49.2-1
- New package: official kitty 0.49.2 x86_64 prebuilt bundle under
  /opt/kitty-0.49.2, with /opt/kitty, /usr/bin/kitty and /usr/bin/kitten
  symlinks, desktop files, icons, man pages, docs and xterm-kitty terminfo.
- kitty is not in LFS/BLFS (user-approved prebuilt exception).
