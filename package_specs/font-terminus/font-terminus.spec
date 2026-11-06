# Terminus is a clean fixed-width bitmap font family.  The classic upstream
# tarball ships console PSFs and X11 PCFs; the TerminusTTF zip is the
# upstream TrueType port of the same 4.49 series (Ax86, OFL).  Payload is
# preserved exactly as released: no strip, AutoProv/AutoReq off.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       font-terminus
Version:    4.49.1
Release:    1
Summary:    Terminus Font: fixed-width bitmap + TrueType set (X11 + console)
License:    OFL
Prefix:     /usr
Source0:    terminus-font-%{version}.tar.gz
Source1:    terminus-ttf-4.49.3.tar.gz

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

BuildRequires: bdftopcf
BuildRequires: mkfontscale
BuildRequires: fontconfig

%description
Terminus Font is a clean, sharp fixed-width bitmap font family designed for
long (8+ hours daily) work sessions.  It supports 1326 characters across
roughly 120 language sets (Latin, Greek, Cyrillic, Hebrew, Armenian, Turkish
etc.), in ten sizes across every available width.  This package ships the
upstream 4.49.1 build: console .psf.gz files for setfont, X11 .pcf.gz
bitmaps for direct X/core-protocol use, and the TrueType port of the same
artwork (TerminusTTF 4.49.3) for fontconfig-based applications that expect
bold/italic faces and per-pixel rendering tags.

Neither terminus-font nor TerminusTTF is in the current base set.
The user explicitly requested packaging them as exceptions to the Tenko
version-policy rule.

Terminus switched to the SIL Open Font License at version 4.40; the
COPYING/OFL.TXT files ship in the payload's doc directory and are the
authoritative license text.  TerminusTTF includes its own COPYING.

%prep
%setup -q -n terminus-font-%{version} -a 1

%build
# Terminus' own configure accepts --prefix; the X11 bitmap pcfs are the
# default targets of the upstream Makefile.
%configure --x11dir=%{_datadir}/fonts/terminus
%make_build

%install
rm -rf %{buildroot}
%make_install
# fonts.dir/fonts.scale for the X11 bitmap path; fontconfig scans the tree
# on its own, so no fc-cache scriptlet is needed (the running system does
# it once at install time from the repository tooling, NOT from rpm).
make fontdir DESTDIR=%{buildroot} || true

# TerminusTTF payloads
install -d -m 0755 %{buildroot}%{_datadir}/fonts/terminus/ttf
for t in TerminusTTF-4.49.3.ttf TerminusTTF-Bold-4.49.3.ttf \
         TerminusTTF-Italic-4.49.3.ttf TerminusTTF-Bold-Italic-4.49.3.ttf; do
    install -m 0644 terminus-ttf-4.49.3/$t \
        %{buildroot}%{_datadir}/fonts/terminus/ttf/$t
done
install -m 0644 terminus-ttf-4.49.3/COPYING \
    %{buildroot}%{_datadir}/fonts/terminus/ttf/COPYING
# 75-yes-terminus.conf: upstream fontconfig hint to make the family
# usable as a terminal font without per-user tweaking.
install -D -m 0644 75-yes-terminus.conf \
    %{buildroot}%{_sysconfdir}/fonts/conf.d/75-yes-terminus.conf

for doc in COPYING OFL.TXT README; do
    [ -f $doc ] || continue
    install -D -m 0644 $doc %{buildroot}%{_datadir}/doc/font-terminus/$doc
done

%files -f %{_sourcedir}/font-terminus.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.49.1
- Rebuild at the current upstream release 4.49.1 (was 4.48) with the
  TerminusTTF 4.49.3 port packaged in the same payload
- Static %files filelist, OFL license text, upstream fontconfig snippet
