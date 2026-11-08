# Noto Emoji is the monochrome (black-and-white) emoji font from the Noto
# project.  Unlike Noto Color Emoji it is an outline variable font, which is
# what the kmscon freetype backend can render into the console cell grid.
# The GUI gets the color font from font-noto-color-emoji; this package stays
# in the base system so the text console has emoji coverage too.
%global __strip /bin/true
%global __spec_install_post %{nil}
%global debug_package %{nil}

Name:       font-noto-emoji
Version:    3.002
Release:    1
Summary:    Noto Emoji: monochrome emoji font
License:    OFL-1.1
URL:        https://github.com/googlefonts/emoji-bw
Prefix:     /usr
Source0:    NotoEmoji-VariableFont_wght.ttf
Source1:    notoemoji-OFL.txt

ExclusiveArch: x86_64

AutoProv: no
AutoReq: no

%description
Noto Emoji is the monochrome member of the Noto emoji family: a variable
weight (300-700) outline font with Unicode emoji coverage.  It is installed
as a weak fallback for the generic families so an emoji character is drawn
rather than replaced by tofu.

The monochrome face is intentional for the text console: kmscon's freetype
backend renders an 8-bit coverage bitmap per glyph, so a color (CBDT/COLR)
emoji face would be copied into the console as scrambled pixels.  The
desktop set additionally installs font-noto-color-emoji for GUI applications.

Version 3.002 is the current Google Fonts build (font table version); the
upstream archive is googlefonts/emoji-bw v3.000.  OFL-1.1 text ships in the
payload.

%prep

%build

%install
rm -rf %{buildroot}
install -d -m 0755 %{buildroot}%{_datadir}/fonts/noto-emoji
install -m 0644 %{SOURCE0} \
    %{buildroot}%{_datadir}/fonts/noto-emoji/NotoEmoji-VariableFont_wght.ttf
install -d -m 0755 %{buildroot}%{_datadir}/doc/font-noto-emoji
install -m 0644 %{SOURCE1} %{buildroot}%{_datadir}/doc/font-noto-emoji/OFL.txt
install -D -m 0644 %{_sourcedir}/69-tenko-noto-emoji.conf \
    %{buildroot}%{_sysconfdir}/fonts/conf.d/69-tenko-noto-emoji.conf

%files -f %{_sourcedir}/font-noto-emoji.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 3.002
- Package the monochrome Noto Emoji variable font from the current Google
  Fonts build, as a generic-family fallback for the console and GUI.  The
  color face is a separate package because kmscon's freetype backend renders
  monochrome coverage bitmaps only.
